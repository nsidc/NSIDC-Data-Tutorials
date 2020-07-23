import os
from base64 import b64encode
import requests
from joblib import Parallel, delayed
from datetime import datetime
from ipyleaflet import Map
import ipywidgets as widgets
from IPython.display import Javascript
from cmr import GranuleQuery
from requests.auth import HTTPBasicAuth

from valkyrie_controls import (epoch_control, dates_slider_control, draw_control, cmr_counts_control,
                               projection_control, itrf_control, datasets_control, projections,
                               nasa_password_control, nasa_username_control, nasa_set_credentials_control)



class valkyrie_ui:

    def __init__(self, hemisphere):
        """
        Interface to talk to the Valkyrie API. The UI renders the northern hemisphere by default
        The UI can be rendered with the render() method.
        You can use the state of the widgets to place order(s) to Valkyrie or use the method directly.
        """
        self.properties = {
            'start_date': datetime(1993, 1, 1),
            'end_date': datetime(2020, 1, 1),
            'ITRF': [None, 'ITRF2000', 'ITRF2008', 'ITRF2014'],
            'polygon': '',
            'hemisphere': hemisphere
        }
        self.session = None
        self.credentials = None

        self.hermes_api_url = 'https://staging.nsidc.org/apps/orders/api'
        self.valkyrie_api_url = 'http://staging.valkyrie-vm.apps.nsidc.org/1.0'

        self.granules = []
        self.projections = projections
        self.h = projection_control(self.properties)
        self.dc = draw_control(self.properties)
        self.date_range = dates_slider_control(self.properties)
        self.epoch = epoch_control(self.properties)
        self.epoch_control = widgets.HBox([widgets.Label('Epoch:'),
                                           self.epoch])
        self.itrf = itrf_control(self.properties)
        self.itrf_control = widgets.HBox([widgets.Label('ITRF:'),
                                            self.itrf])
        self.datasets = datasets_control(self.properties)

        self.granule_count = cmr_counts_control(self.properties)
        self.granule_count.on_click(self.query_cmr)

        self.components = [self.h,
                           self.datasets,
                           self.itrf_control,
                           self.epoch_control,
                           self.date_range]
        self.username = nasa_username_control(None)
        self.password = nasa_password_control(None)
        self.credentials_button = nasa_set_credentials_control(None)
        self.credentials_button.on_click(self.set_credentials)


    def set_credentials(self, event):
        if (self.username.value != '' and self.password.value != ''):
            self.credentials = {
                'username': self.username.value,
                'password': self.password.value
            }
            session = self.create_earthdata_authenticated_session()
            if session is None:  # type: ignore
                print('Invalid credentials')
                self.credentials = None
            else:
                print(f'Logged in to NASA EarthData with username: {self.credentials["username"]}')

        else:
            print('enter your NASA Earth login credentials')
            self.credentials = None
            return None


    def render_credentials(self):
        display(self.username, self.password, self.credentials_button)


    def render(self):
        max_zoom = 8
        if self.h.value != 'global':
            max_zoom = 4
        self.map = Map(center=self.projections[self.h.value]['center'],
                       zoom=1,
                       max_zoom=max_zoom,
                       basemap=self.projections[self.h.value]['base_map'],
                       crs=self.projections[self.h.value]['projection'])

        self.map.add_control(self.dc)
        self.map.layout.height = '600px'
        for component in self.components:
            display(component)
        display(self.map)
        display(self.granule_count)


    def bounding_box(self, points):
        x_coordinates, y_coordinates = zip(*points)
        return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]


    def build_params(self):
        self.datasets_valkyrie = []
        if self.dc.last_draw['geometry'] is None:
            print('You need to select an area using the box tool')
            return None
        coords = [list(coord) for coord in self.bounding_box(self.dc.last_draw['geometry']['coordinates'][0])]
        bbox = f'{coords[0][0]},{coords[0][1]},{coords[1][0]},{coords[1][1]}'
        start = self.date_range.value[0].date().strftime('%Y-%m-%d')
        end = self.date_range.value[1].date().strftime('%Y-%m-%d')
        ITRF = self.itrf.value
        epoch = self.epoch.value
    #     if (d2-d1).days > 180:
    #         print('Remember this is a tutorial, if you want more than a year of data please contact NSIDC support')
    #         print('...Adjust the time range slider and try again!')
    #         return None
        if 'ATM' in self.datasets.value:
            self.datasets_valkyrie.append('ATM1B')
        if 'GLAH06' in self.datasets.value:
            self.datasets_valkyrie.append('GLAH06')
        if 'ILVIS2' in self.datasets.value:
            self.datasets_valkyrie.append('ILVIS2')
        params = {
            'start': start,
            'end': end,
            'bbox': bbox
        }
        if ITRF != 'None' and ITRF != None:
            params['itrf'] = ITRF

        if epoch != 'None' and epoch != '':
            params['epoch'] = epoch
        return params


    def query_cmr(self, params):
        if self.dc.last_draw['geometry'] is None:
            print('You need to select an area using the box tool')
            return None
        self.granules = {}
        datasets_cmr = []
        d1 = self.date_range.value[0].date()
        d2 = self.date_range.value[1].date()
        coords = [list(coord) for coord in self.bounding_box(self.dc.last_draw['geometry']['coordinates'][0])]
        bbox = (coords[0][0],coords[0][1],coords[1][0],coords[1][1])
        if 'ATM' in self.datasets.value:
            datasets_cmr.extend([{'name':'ILATM1B'},{'name':'BLATM1B'}])
        if 'GLAH06' in self.datasets.value:
            datasets_cmr.append({'name':'GLAH06'})
        if 'ILVIS2' in self.datasets.value:
            datasets_cmr.append({'name': 'ILVIS2'})

        for d in datasets_cmr:
            cmr_api = GranuleQuery()
            g = cmr_api.parameters(
                short_name=d['name'],
                temporal=(d1,d2),
                bounding_box = bbox).get_all()
            self.granules[d['name']] = g
        if params is not None:
            for dataset in self.granules:
                size = round(sum(float(g['granule_size']) for g in self.granules[dataset]), 2)
                print(f'{dataset}: {len(self.granules[dataset])} granules found. Approx download size: {size} MB')
        return self.granules


    def download_cmr_granules(self, dataset, start, end):
        if self.granules is None:
            return None
        file_paths = []
        Parallel(n_jobs=8, backend="threading")(
            delayed(self.download_cmr_granule)(g['url'],file_paths) for g in self.granules[dataset][start:end]
        )
        return file_paths


    def download_cmr_granule(self, url, file_paths):
        local_filename = url.split('/')[-1]
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            if not os.path.exists(f'data/{local_filename}'):
                with open('data/' + local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                file_paths.append(local_filename)
        return local_filename


    def post_data_orders(self, params, service):
        if self.session is None or self.credentials is None:
            print('You need to login into NASA EarthData before placing a Valkyrie Order')
            return None
        params = self.build_params()
        hermes_params = None
        username = self.credentials['username']

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
        if self.session is None or self.credentials is None:
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
        if dataset in ['ILATM1B','BLATM1B', 'ATM']:
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
        "fulfillment": "valkyrie",
        "delivery": "valkyrie",
        "uid": f"{username}"
        }
        if 'itrf' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_itrf'] = params['itrf']

        if 'epoch' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_epoch'] = params['epoch']

        base_url = f'{self.hermes_api_url}/orders/'
        self.session.headers['referer'] = 'https://hermes.apps.int.nsidc.org/api/'
        # self.session.headers['referer'] = 'https://valkyrie.request'
        order['request'] = hermes_params
        order['response'] = self.session.post(base_url,
                                              json=hermes_params,
                                              verify=False)
        # now we are going to return the response from Valkyrie
        return order


    def create_earthdata_authenticated_session(self):
        s = requests.session()
        auth_url = f'{self.hermes_api_url}/earthdata/auth/'
        # print(auth_url)
        nsidc_resp = s.get(auth_url, timeout=10, allow_redirects=True)
        auth_cred = HTTPBasicAuth(self.credentials['username'], self.credentials['password'])
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




