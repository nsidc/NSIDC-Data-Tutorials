import requests
from joblib import Parallel, delayed
from datetime import datetime
from ipyleaflet import Map
import ipywidgets as widgets
from IPython.display import Javascript
import os


from utils import (north_3413, south_3031, projections, draw_control, projection_control,
                   dates_slider_control, pixels_control, time_delta_control, format_polygon)


class itslive_ui:

    def __init__(self, hemisphere):
        self.properties = {
            'start_date': datetime(1984, 1, 1),
            'end_date': datetime(2020, 1, 1),
            'pixels': 1,
            'time_delta': 0,
            'polygon': '',
            'hemisphere': hemisphere
        }

        self.projections = projections
        self.h = projection_control(self.properties)
        self.dc = draw_control(self.properties)
        self.date_range = dates_slider_control(self.properties)
        self.pixels = pixels_control(self.properties)
        self.pixels_control = widgets.HBox([widgets.Label('Minimum % of valid pixels per image pair:'),
                                            self.pixels])
        self.time_delta = time_delta_control(self.properties)
        self.time_delta_control = widgets.HBox([widgets.Label('Days of separation between image pairs:'),
                                                self.time_delta])

        self.components = [self.h,
                           self.pixels_control,
                           self.time_delta_control,
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


    def update_coverages(self):
        base_url = 'https://staging.itslive-search.apps.nsidc.org/velocities/coverage/'
        params = self.build_params()
        resp = requests.get(base_url, params=params, verify=False)
        self.coverage = resp.json()
        return self.coverage


    def get_granule_urls(self):
        base_url = 'https://staging.itslive-search.apps.nsidc.org/velocities/urls/'
        params = self.build_params()
        # params['compression'] = 'false'
        # params['serialization'] = 'json'
        resp = requests.get(base_url, params=params, verify=False)
        self.urls = resp.json()
        return self.urls


    def get_url_size(self, url, sizes):
        size = 0
        try:
            resp = requests.head(url)
            size = float("{:.2f}".format(int(resp.headers['Content-Length'])/1024))
        except IOError:
            sizes.append(size)
            return
        sizes.append(size)


    def calculate_file_sizes(self, max_urls):
        file_sizes = []
        Parallel(n_jobs=8, backend="threading")(
            delayed(self.get_url_size)(url['url'],file_sizes) for url in self.urls[0:max_urls]
        )
        return file_sizes


    def build_params(self):
        if self.dc.last_draw['geometry'] is None:
            print('You need to select an area using the box tool or the polygon drawing tool')
            return None
        polygon_coords = format_polygon(self.dc.last_draw['geometry'])
        start = self.date_range.value[0].date().strftime('%Y-%m-%d')
        end = self.date_range.value[1].date().strftime('%Y-%m-%d')
        pixels = self.pixels.value

        params = {
            'polygon': polygon_coords,
            'start': start,
            'end': end,
            'percent_valid_pixels': pixels,
        }
        if self.time_delta.value != 'any':
            params['time_delta'] = self.time_delta.value
        return params


    def download_velocity_pairs(self, start, end):
        file_paths = []
        Parallel(n_jobs=8, backend="threading")(
            delayed(self.download_file)(url['url'],file_paths) for url in self.urls[start:end]
        )
        return file_paths


    def download_file(self, url, file_paths):
        local_filename = url.split('/')[-1]
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            if not os.path.exists(f'data/{local_filename}'):
                with open('data/' + local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                file_paths.append(local_filename)
        return local_filename

