import os
from uuid import uuid4
import requests
from joblib import Parallel, delayed
from datetime import datetime
from cmr import GranuleQuery
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from .is2 import is2


class IceflowClient:
    def __init__(self):
        """
        Client class for IceFlow.
        """
        self.properties = {
            'start_date': datetime(1993, 1, 1),
            'end_date': datetime.now(),
            'polygon': '',
            'bbox': ''
        }
        self.session = None
        self.icesat2 = None
        # IceFlow uses Hermes, the NSIDC data ordering API as a proxy
        self.hermes_api_url = 'https://nsidc.org/apps/orders/api'
        self.granules = []

    def valid_session(self):
        if self.session is None:
            print('You need to login into NASA EarthData before placing an IceFLow Order')
            return None
        return True

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

    def _get_dataset_latest_version(self, dataset):
        """
        Returns the latest version of a NSIDC-DAAC dataset
        """
        try:
            metadata = requests.get(f'http://nsidc.org/api/dataset/metadata/v2/{dataset}.json').json()
            latest_version = metadata['newestPublishedMajorVersion']
        except Exception:
            print('dataset not found')
            return None
        if dataset.startswith('ATL'):
            version = f"{str(latest_version).zfill(3)}"
        else:
            version = latest_version
        return version

    def bounding_box(self, points):
        """
        returns a bbox array for a given polygon
        """
        x_coordinates, y_coordinates = zip(*points)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

    def _expand_datasets(self, params):
        """
        IceFlow consolidates ATM1B and CMR does not. We need to expand the dataset
        names and versions.
        """
        cmr_datasets = []
        bbox = [float(coord) for coord in params['bbox'].split(',')]
        temporal = (datetime.strptime(params['start'], '%Y-%m-%d'),
                    datetime.strptime(params['end'], '%Y-%m-%d'))
        bbox = (bbox[0], bbox[1], bbox[2], bbox[3])
        for d in params['datasets']:
            if d == 'ATM1B':
                cmr_datasets.extend([{'name': 'ILATM1B',
                                      'version': None,
                                      'temporal': temporal,
                                      'bounding_box': bbox},
                                    {'name': 'BLATM1B',
                                     'version': None,
                                     'temporal': temporal,
                                     'bounding_box': bbox}])
            elif d == 'GLAH06' or d == 'ILVIS2':
                cmr_datasets.append({'name': d,
                                     'version': None,
                                     'temporal': temporal,
                                     'bounding_box': bbox})

            else:
                latest_version = self._get_dataset_latest_version(d)
                cmr_datasets.append({'name': d,
                                     'version': latest_version,
                                     'temporal': temporal,
                                     'bounding_box': bbox})
        return cmr_datasets

    def query_cmr(self, params=None):
        """
        Queries CMR for one or more data sets short-names using the spatio-temporal
        constraints defined in params. Returns a json list of CMR records.
        """
        if params is None:
            return None
        self.granules = {}
        datasets = self._expand_datasets(params)
        for d in datasets:
            cmr_api = GranuleQuery()
            g = cmr_api.parameters(
                short_name=d['name'],
                version=d['version'],
                temporal=d['temporal'],
                bounding_box=d['bounding_box']).get_all()
            self.granules[d['name']] = g

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
            if dataset in ['ATM1B', 'ILATM1B', 'BLATM1B']:
                dataset = 'ATM1B'  # IceFlow consolidates ATM data
            provider = 'valkyrie'

        return {
            'dataset': dataset,
            'start': params['start'],
            'end': params['end'],
            'bbox': params['bbox'],
            'provider': provider
        }

    def place_data_orders(self, params):
        """
        Post a data order to either Iceflow or EGI (Icepyx).
        """
        if self.valid_session() is None:
            return None
        if params is None:
            print('You need to pass spatio temporal parameters')
            return None
        orders = []
        for dataset in params['datasets']:
            order_parameters = self._parse_order_parameters(dataset, params)
            if order_parameters['provider'] == 'icepyx':
                order = self._post_icepyx_order(order_parameters)
            else:
                order = self._post_iceflow_order(order_parameters)
            orders.append(order)
        return orders

    def check_order_status(self, order):
        if self.valid_session() is None:
            return None
        if order['provider'] == 'icepyx':
            return {
                'status': 'COMPLETE',
                'url': None
            }
        else:
            order_id = order['response']['order']['order_id']
            status_url = f'{self.hermes_api_url}/orders/{order_id}'
            response = self.session.get(status_url).json()
            status = response['status'].upper()
            if status == 'COMPLETE':
                granule_url = response['file_urls']['data'][0]
                granule_url = granule_url.replace('int.nsidc', 'nsidc')
            else:
                granule_url = None
            response = {
                'status': status,
                'url': granule_url
            }
            return response

    def _post_icepyx_order(self, params):
        """
        Icepyx uses a sync method to download granules, so there is no place order per se,
        instead we just query for the granules and then download them.
        """
        self.is2_query = self.icesat2.query(params)
        return {
            'id': uuid4(),
            'provider': 'icepyx',
            'dataset': params['dataset'],
            'request': params,
            'response': self.is2_query,
            'status': 'PENDING'
        }

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
            hermes_params['selection_criteria']['filters']['valkyrie_itrf'] = params['itrf']

        if 'epoch' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_epoch'] = params['epoch']

        base_url = f'{self.hermes_api_url}/orders/'
        self.session.headers['referer'] = 'https://valkyrie.request'
        response = self.session.post(base_url,
                                     json=hermes_params,
                                     verify=False).json()
        order = {
            'id': response['order']['order_id'],
            'provider': 'iceflow',
            'dataset': params['dataset'],
            'request': hermes_params,
            'response': response,
            'status': 'PENDING'
        }
        # now we are going to return the response from Hermes
        return order

    def _create_earthdata_authenticated_session(self):
        s = requests.session()
        auth_url = f'{self.hermes_api_url}/earthdata/auth/'
        nsidc_resp = s.get(auth_url, timeout=10, allow_redirects=False)        
        auth_cred = HTTPBasicAuth(self.credentials['username'], self.credentials['password'])
        auth_resp = s.get(nsidc_resp.headers['Location'],
                          auth=auth_cred,
                          allow_redirects=True,
                          timeout=10)
        
        if not (auth_resp.ok):  # type: ignore
            if auth_resp.status_code == 404 or auth_resp.status_code == 500:
                # HERMES bug
                self.session = s
                # Now we create a icesat2 instance so we can query for ATL data using icepyx
                self.icesat2 = is2(self.credentials)
                return self.session

            print(nsidc_resp.url)
            print(f'Authentication with Earthdata Login failed first with:\n{auth_resp.text}')
            return None
        
        else:  # type: ignore
            self.session = s
            # Now we create a icesat2 instance so we can query for ATL data using icepyx
            self.icesat2 = is2(self.credentials)
            return self.session

    def h5_filename(self, order):
        dataset = order['dataset']
        order_id = order['id']
        today = datetime.today().strftime('%Y%m%d')
        return f'{dataset}-{today}-{order_id}'

    def download_orders(self, orders):
        for order in orders:
            dataset = order['dataset']
            status = self.check_order_status(order)
            print(f"dataset: {dataset}, order {order['id']} status is {status['status']}")
            if status['status'] == 'COMPLETE' and order['status'] != 'DOWNLOADED':
                print(' >> Downloading order...')
                data_granule = self.download_order(order)
                print(f' >> Order Downloaded: {data_granule}')
            elif status['status'] == 'COMPLETE' and order['status'] == 'DOWNLOADED':
                print(f"order {order['id']} for {dataset} has been downloaded already")

    def download_order(self, order):
        if order['provider'] == 'icepyx' and order['status'] != 'DOWNLOADED':
            granules = order['response'].download_granules('./data')
            order['status'] = 'DOWNLOADED'
            return granules
        else:
            status = self.check_order_status(order)
            filename = self.h5_filename(order)
            if status['status'] == 'COMPLETE' and order['status'] != 'DOWNLOADED':
                granule = self.download_hdf5(status['url'], filename)
                order['status'] = 'DOWNLOADED'
                return granule

    def download_hdf5(self, url, file_name=None):
        url = url.replace('int.nsidc', 'nsidc')
        order_data = requests.get(url, stream=True)
        total_size_in_bytes = int(order_data.headers.get('content-length', 0))
        if file_name == '' or file_name is None:
            file_name = url.split('/')[-1].replace('.hdf5', '')
        # check if file exist.
        if os.path.isfile(f'data/{file_name}.h5'):
            print('File already downloaded, skipping...')
            return None
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        # download in 1MB chunks
        with open(f'data/{file_name}.h5', 'wb') as f:
            for chunk in order_data.iter_content(chunk_size=1048576):
                progress_bar.update(len(chunk))
                if chunk:
                    f.write(chunk)
        progress_bar.close()
        print(f'Granule downloaded: data/{file_name}.h5')
        return f'data/{file_name}.h5'
