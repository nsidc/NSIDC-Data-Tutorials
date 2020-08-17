import os
import requests
from joblib import Parallel, delayed
from datetime import datetime
from cmr import GranuleQuery
from requests.auth import HTTPBasicAuth

from .controls import ValkyrieUI


class ValkyrieClient:
    def __init__(self):
        """
        Interface to talk to the Valkyrie API. The UI renders the northern hemisphere by default
        The UI can be rendered with the render() method.
        You can use the state of the widgets to place order(s) to Valkyrie or use the method directly.
        """
        self.properties = {
            'start_date': datetime(1993, 1, 1),
            'end_date': datetime(2021, 1, 1),
            'polygon': '',
            'hemisphere': 'north'
        }
        self.session = None
        self.credentials = None
        self.hermes_api_url = 'https://staging.nsidc.org/apps/orders/api'
        self.valkyrie_api_url = 'http://staging.valkyrie-vm.apps.nsidc.org/1.0'
        self.granules = []
        self.controls = ValkyrieUI(self.properties)

    def bounding_box(self, points):
        x_coordinates, y_coordinates = zip(*points)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

    def build_params(self):
        """
        returns the current selection parameters based on the widgets and map state
        """
        self.datasets_valkyrie = []
        if self.controls.dc.last_draw['geometry'] is None:
            print('You need to select an area using the box tool')
            return None
        coords = [list(coord) for coord in self.bounding_box(self.controls.dc.last_draw['geometry']['coordinates'][0])]
        bbox = f'{coords[0][0]},{coords[0][1]},{coords[1][0]},{coords[1][1]}'
        start = self.controls.dates_range.value[0].date().strftime('%Y-%m-%d')
        end = self.controls.dates_range.value[1].date().strftime('%Y-%m-%d')
        ITRF = self.controls.itrf.value
        epoch = self.controls.epoch.value
        datasets = self.controls.dataset.value

        if 'ATM' in datasets:
            self.datasets_valkyrie.append('ATM1B')
        if 'GLAH06' in datasets:
            self.datasets_valkyrie.append('GLAH06')
        if 'ILVIS2' in datasets:
            self.datasets_valkyrie.append('ILVIS2')
        params = {
            'start': start,
            'end': end,
            'bbox': bbox
        }
        if ITRF != 'None' and ITRF is not None:
            params['itrf'] = ITRF

        if epoch != 'None' and epoch != '':
            params['epoch'] = epoch
        return params

    def _query_cmr_(self):
        datasets = self.controls.dataset.value
        if self.controls.dc.last_draw['geometry'] is None:
            print('You need to select an area using the box tool')
            return None
        self.granules = {}
        datasets_cmr = []
        d1 = self.controls.dates_range.value[0].date()
        d2 = self.controls.dates_range.value[1].date()
        coords = [list(coord) for coord in self.bounding_box(self.controls.dc.last_draw['geometry']['coordinates'][0])]
        bbox = (coords[0][0], coords[0][1], coords[1][0], coords[1][1])
        if 'ATM' in datasets:
            datasets_cmr.extend([{'name': 'ILATM1B'}, {'name': 'BLATM1B'}])
        if 'GLAH06' in datasets:
            datasets_cmr.append({'name': 'GLAH06'})
        if 'ILVIS2' in datasets:
            datasets_cmr.append({'name': 'ILVIS2'})

        for d in datasets_cmr:
            cmr_api = GranuleQuery()
            g = cmr_api.parameters(
                short_name=d['name'],
                temporal=(d1, d2),
                bounding_box=bbox).get_all()
            self.granules[d['name']] = g
        return self.granules

    def query_cmr(self, datasets=[], params=None):
        """
        Queries CMR for one or more data sets short-names using the spatio-temporal constraints defined in params.
        Returns a json list of CMR records.
        """
        if params is None:
            return self._query_cmr_()
        self.granules = {}

        for d in datasets:
            cmr_api = GranuleQuery()
            g = cmr_api.parameters(
                short_name=d,
                temporal=(params['start'], params['end']),
                bounding_box=params['bbox']).get_all()
            self.granules[d] = g

        return self.granules

    def cmr_download_size(self, granules):
        sizes = {}
        for dataset in granules:
            size = round(sum(float(g['granule_size']) for g in self.granules[dataset]), 2)
            sizes[dataset] = size
            print(f'{dataset}: {len(self.granules[dataset])} granules found. Approx download size: {size} MB')
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

    def post_data_orders(self, params, service='valkyrie'):
        """
        Post a data order to either Valkyrie or Hermes. Talking directly to Hermes will be deprecated soon.
        """
        if self.session is None or self.credentials is None:
            print('You need to login into NASA EarthData before placing a Valkyrie Order')
            return None
        if params is None:
            params = self.build_params()
        responses = []
        for dataset in self.datasets_valkyrie:
            if service == 'valkyrie':
                resp = self.post_valkyrie_order(params)
            elif service == 'hermes':
                resp = self.post_hermes_order(params)
            else:
                print('service not registered, plase use valkyrie or hermes')
                return None
            responses.append(resp)

        return responses

    def post_valkyrie_order(self, params):
        order = {}
        if self.session is None:
            print('You need to use your NASA Earth Credentials, see instructions above')
            return None
        valkyrie_params = {
            "bbox": params['bbox'],
            "time_range": f"{params['start']},{params['end']}"
        }
        if 'itrf' in params:
            valkyrie_params['itrf'] = params['itrf']

        if 'epoch' in params:
            valkyrie_params['epoch'] = params['epoch']
        dataset = params['dataset']
        if dataset in ['ILATM1B', 'BLATM1B', 'ATM']:
            dataset = 'ATM1B'

        base_url = f'{self.valkyrie_api_url}/{dataset}'
        # self.session.headers['referer'] = 'https://hermes.apps.int.nsidc.org/api/'
        # self.session.headers['referer'] = 'https://valkyrie.request'
        order['request'] = valkyrie_params
        order['response'] = requests.post(base_url,
                                          params=valkyrie_params)
        # now we are going to return the response from Valkyrie
        return order

    def post_hermes_order(self, params):
        order = {}
        if self.session is None or self.credentials is None:
            print('You need to use your NASA Earth Credentials, see instructions above')
            return None
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
            hermes_params['selection_criteria']['filters']['valkyrie_itrf'] = params['itrf']

        if 'epoch' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_epoch'] = params['epoch']

        base_url = f'{self.hermes_api_url}/orders/'
        # TODO: Need to implement a client regex and refactor Hermes
        self.session.headers['referer'] = 'https://hermes.apps.int.nsidc.org/api/'
        # self.session.headers['referer'] = 'https://valkyrie.request'
        order['request'] = hermes_params
        order['response'] = self.session.post(base_url,
                                              json=hermes_params,
                                              verify=False)
        # now we are going to return the response from Hermes
        return order

    def create_earthdata_authenticated_session(self, user=None, password=None):
        s = requests.session()
        auth_url = f'{self.hermes_api_url}/earthdata/auth/'
        nsidc_resp = s.get(auth_url, timeout=10, allow_redirects=True)
        if user is None and password is None:
            user = self.controls.credentials['username']
            password = self.controls.credentials['password']
        auth_cred = HTTPBasicAuth(user, password)
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

    def display(self, what, where='horizontal', hemisphere='north', extra_layers=False):
        if 'credentials' in what:
            self.controls.display_credentials(where)
        if 'controls' in what:
            self.controls.display_controls(where)
        if 'map' in what:
            self.controls.display_map(where, hemisphere, extra_layers)


