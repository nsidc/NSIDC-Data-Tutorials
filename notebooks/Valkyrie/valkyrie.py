import os
import requests
from joblib import Parallel, delayed
from datetime import datetime
from ipyleaflet import Map
import ipywidgets as widgets
from IPython.display import Javascript
from cmr import GranuleQuery


from valkyrie_controls import (epoch_control, dates_slider_control, draw_control, cmr_counts_control,
                   projection_control, itrf_control, datasets_control, projections)



class valkyrie_ui:

    def __init__(self, hemisphere):
        self.properties = {
            'start_date': datetime(1993, 1, 1),
            'end_date': datetime(2020, 1, 1),
            'ITRF': [None, 'ITRF2000', 'ITRF2008', 'ITRF2014'],
            'polygon': '',
            'hemisphere': hemisphere
        }

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


    def render(self):
        self.map = Map(center=self.projections[self.h.value]['center'],
                       zoom=1,
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


    def set_earthdata_user(self, username):
        self.user = username


    def query_cmr(self, event):
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
        if event is not None:
            print(self.granules)
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


    def post_valkyrie_orders(self):
        params = self.build_params()
        hermes_params = None

        responses = []
        for dataset in self.datasets_valkyrie:
            hermes_params = {
            "selection_criteria": {
                "filters": {
                    "bounding_box": params['bbox'],
                    "dataset_short_name": dataset,
                    "time_start": params['start'],
                    "time_end": params['end']
                }
            },
            "fulfillment": "valkyrie",
            "delivery": "valkyrie",
            "uid": self.username
            }
            if 'itrf' in params:
                hermes_params['selection_criteria']['filters']['valkyrie_itrf'] = params['itrf']

            if 'epoch' in params:
                hermes_params['selection_criteria']['filters']['valkyrie_epoch'] = params['epoch']


            base_url = 'https://staging.hermes.apps.int.nsidc.org/api/'
            response = requests.post(base_url, json=hermes_params)
            # now we are going to return the response from Valkyrie
            responses.append({d: response.json()})
        return responses


    def post_valkyrie_order(self, params):
        hermes_params = {
        "selection_criteria": {
            "filters": {
                "bounding_box": params['bbox'],
                "dataset_short_name": params['dataset'],
                "time_start": params['start'],
                "time_end": params['end']
            }
        },
        "fulfillment": "valkyrie",
        "delivery": "valkyrie",
        "uid": self.username
        }
        if 'itrf' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_itrf'] = params['itrf']

        if 'epoch' in params:
            hermes_params['selection_criteria']['filters']['valkyrie_epoch'] = params['epoch']

        base_url = 'https://staging.hermes.apps.int.nsidc.org/api/'
        response = requests.post(base_url, json=hermes_params)
        # now we are going to return the response from Valkyrie
        return response
