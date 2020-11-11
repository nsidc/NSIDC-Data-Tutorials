import os
import requests
from joblib import Parallel, delayed
from datetime import datetime
from cmr import GranuleQuery
from requests.auth import HTTPBasicAuth
from .is2 import is2


class IceflowClient:
    def __init__(self):
        """
        Interface to talk to the IceFlow API. The UI renders the northern hemisphere by default
        The UI can be rendered with the render() method.
        You can use the state of the widgets to place order(s) to Valkyrie or use the method directly.
        """
        self.properties = {
            'start_date': datetime(1993, 1, 1),
            'end_date': datetime.now(),
            'polygon': '',
            'bbox': ''
        }
        self.session = None
        self.icesat2 = None
        self.hermes_api_url = 'https://nsidc.org/apps/orders/api'
        self.iceflow_api_url = 'http://valkyrie-vm.apps.nsidc.org/1.0'
        self.granules = []

    def authenticate(self, user, password, email):
        if user is not None and password is not None:
            self.credentials = {
                'username': user,
                'password': password,
                'email': email
            }
        else:
            print('user and password must have valid values')
            return None
        return self._create_earthdata_authenticated_session()

    def bounding_box(self, points):
        """
        returns a bbox array for a given polygon
        """
        x_coordinates, y_coordinates = zip(*points)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

    def query_cmr(self, params=None):
        """
        Queries CMR for one or more data sets short-names using the spatio-temporal
        constraints defined in params. Returns a json list of CMR records.
        """
        if params is None:
            return None
        self.granules = {}
        bbox = [float(coord) for coord in params['bbox'].split(',')]
        for d in params['datasets']:
            cmr_api = GranuleQuery()
            g = cmr_api.parameters(
                short_name=d,
                temporal=(datetime.strptime(params['start'], '%Y-%m-%d'),
                          datetime.strptime(params['end'], '%Y-%m-%d')),
                bounding_box=(bbox[0], bbox[1], bbox[2], bbox[3])).get_all()
            self.granules[d] = g

        self.cmr_download_size(self.granules)
        return self.granules

    def cmr_download_size(self, granules):
        sizes = {}
        for dataset in granules:
            size = round(sum(float(g['granule_size']) for g in self.granules[dataset]) / 1024, 2)
            sizes[dataset] = size
            print(f'{dataset}: {len(self.granules[dataset])} granules found. Approx download size: {size} GB')
        return sizes

    def download_cmr_granules(self, dataset, start, end):
        """
        Downloads granules (data files) directly form their CMR source.
        Note that this can bring a lot of data and is only adviced to be used when you have a small
        selection and plenty of space in the hard drive.
        """
        if self.granules is None:
            return None
        file_paths = []
        Parallel(n_jobs=8, backend="threading")(
            delayed(self._download_cmr_granule)(g['url'], file_paths) for g in self.granules[dataset][start:end]
        )
        return file_paths

    def _download_cmr_granule(self, url, file_paths):
        local_filename = url.split('/')[-1]
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            if not os.path.exists(f'data/{local_filename}'):
                with open('data/' + local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                file_paths.append(local_filename)
        return local_filename

    def _parse_order_parameters(self, dataset, params):
        if dataset in ['ATL03', 'ATL06', 'ATL07', 'ATL08']:
            provider = 'icepyx'
        else:
            provider = 'valkyrie'

        return {
            'dataset': dataset,
            'start': params['start'],
            'end': params['end'],
            'bbox': params['bbox'],
            'provider': provider
        }

    def post_data_orders(self, params):
        """
        Post a data order to either Iceflow or EGI (Icepyx).
        """
        if self.session is None:
            print('You need to login into NASA EarthData before placing an IceFLow Order')
            return None
        if params is None:
            print('You need to pass spatio temporal parameters')
            return None
        responses = []
        for dataset in params['datasets']:
            order_parameters = self._parse_order_parameters(dataset, params)
            if order_parameters['provider'] == 'icepyx':
                resp = self._post_icepyx_order(order_parameters)
            else:
                resp = self._post_iceflow_order(order_parameters)
            responses.append(resp)

        return responses

    def _post_icepyx_order(self, params):
        is2_query = self.icesat2.query(params)
        # Looks like this is synchronous, we need to fork icepyx to improve it.
        is2_query.download_granules('./data')

    def _post_iceflow_order(self, params):
        order = {}
        username = self.credentials['username']
        if 'provider' in params:
            provider = params['provider']
        else:
            provider = 'valkyrie'
        hermes_params = {
            "selection_criteria": {
                "filters": {
                    "dataset_short_name": params['dataset'],
                    "dataset_version": "1",
                    "bounding_box": params['bbox'],
                    "time_start": params['start'],
                    "time_end": params['end']
                }
            },
            "fulfillment": provider,
            "delivery": provider,
            "uid": f"{username}"
        }
        if 'itrf' in params:
            hermes_params['selection_criteria']['filters']['iceflow_itrf'] = params['itrf']

        if 'epoch' in params:
            hermes_params['selection_criteria']['filters']['iceflow_epoch'] = params['epoch']

        base_url = f'{self.hermes_api_url}/orders/'
        self.session.headers['referer'] = 'https://valkyrie.request'
        order['request'] = hermes_params
        order['response'] = self.session.post(base_url,
                                              json=hermes_params,
                                              verify=False)
        # now we are going to return the response from Hermes
        return order

    def __post_valkyrie_order(self, params):
        order = {}
        if self.session is None:
            print('You need to use your NASA Earth Credentials, see instructions above')
            return None
        iceflow_params = {
            "bbox": params['bbox'],
            "time_range": f"{params['start']},{params['end']}"
        }
        if 'itrf' in params:
            iceflow_params['itrf'] = params['itrf']

        if 'epoch' in params:
            iceflow_params['epoch'] = params['epoch']
        dataset = params['dataset']
        if dataset in ['ILATM1B', 'BLATM1B', 'ATM']:
            dataset = 'ATM1B'

        base_url = f'{self.iceflow_api_url}/{dataset}'
        # self.session.headers['referer'] = 'https://hermes.apps.int.nsidc.org/api/'
        # self.session.headers['referer'] = 'https://iceflow.request'
        order['request'] = iceflow_params
        order['response'] = requests.post(base_url,
                                          params=iceflow_params)
        # now we are going to return the response from Valkyrie
        return order

    def _create_earthdata_authenticated_session(self):
        s = requests.session()
        auth_url = f'{self.hermes_api_url}/earthdata/auth/'
        nsidc_resp = s.get(auth_url, timeout=10, allow_redirects=True)
        auth_cred = HTTPBasicAuth(self.credentials['user'], self.credentials['password'])
        auth_resp = s.get(nsidc_resp.url,
                          auth=auth_cred,
                          allow_redirects=False,
                          timeout=10)
        if not (auth_resp.ok):  # type: ignore
            print(nsidc_resp.url)
            print(f'Authentication with Earthdata Login failed with:\n{auth_resp.text}')
            return None
        resp_hermes = s.get(auth_resp.headers['Location'], allow_redirects=False)
        if not (resp_hermes.ok):
            print('NSIDC HERMES could not authenticate')
            return resp_hermes
        self.session = s
        # Now we create a icesat2 instance so we can query for ATL data using icepyx
        self.icesat2 = is2(self.credentials)
        return self.session

    def order_status(self, order):
        order_status_url = order['response'].json()['status_url']
        order_status = requests.get(order_status_url).json()
        return order_status

    def download_order(self, url, file_name):
        order_data = requests.get(url, stream=True)
        if file_name == '' or file_name is None:
            file_name = url.split('/')[-1].replace('.hdf5', '')
        with open(f'data/{file_name}.h5', 'wb') as f:
            for chunk in order_data.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return f'data/{file_name}.h5'
