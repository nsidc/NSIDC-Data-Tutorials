import pandas as pd
import ipywidgets as widgets
import itertools
from sidecar import Sidecar
from IPython.display import display
from ipyleaflet import (Map, projections, basemaps, SearchControl, AwesomeIcon,
                        Marker, DrawControl, LayersControl)

from .layers import custom_layers, flight_layers


place_marker = Marker(icon=AwesomeIcon(name="check", marker_color='green', icon_color='darkgreen'))


north_3413 = {
    'name': 'EPSG:3413',
    'custom': True,
    'proj4def': '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    'origin': [-4194304, 4194304],
    'bounds': [
        [-4194304, -4194304],
        [4194304, 4194304]
    ],
    'resolutions': [
        16384.0,
        8192.0,
        4096.0,
        2048.0,
        1024.0,
        512.0,
        256.0
    ]
}

south_3031 = {
    'name': 'EPSG:3031',
    'custom': True,
    'proj4def': '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs',
    'origin': [-4194304, 4194304],
    'bounds': [
        [-4194304, -4194304],
        [4194304, 4194304]
    ],
    'resolutions': [
        16384.0,
        8192.0,
        4096.0,
        2048.0,
        1024.0,
        512.0,
        256.0
    ]
}

projections = {
    'global': {
        'base_map': basemaps.NASAGIBS.BlueMarble,
        'projection': projections.EPSG3857,
        'center': (30, -30),
        'zoom': 2,
        'max_zoom': 8
    },
    'north': {
        'base_map': basemaps.NASAGIBS.BlueMarble3413,
        'projection': north_3413,
        'center': (80, -50),
        'zoom': 1,
        'max_zoom': 4
    },
    'south': {
        'base_map': basemaps.NASAGIBS.BlueMarble3031,
        'projection': south_3031,
        'center': (-90, 0),
        'zoom': 1,
        'max_zoom': 4
    }
}


def format_polygon(geometry):
    coords = [[str(float("{:.4f}".format(coord[0]))),
               str(float("{:.4f}".format(coord[1])))] for coord in geometry['coordinates'][0]]
    coords = list(itertools.chain.from_iterable(coords))
    polygonstr = ','.join(coords)
    return polygonstr


class IceFlowUI:
    """
    builds widgets for the user interface
    """
    def __init__(self, properties, query_cmr, post_iceflow_order):
        self.query_cmr = query_cmr
        self.out = widgets.Output(layout={'border': '1px solid black'})
        self.credentials = None
        self.start_date = properties['start_date']
        self.end_date = properties['end_date']
        self.projections = projections

        slider_dates = [(date.strftime(' %Y-%m-%d '), date) for date in
                        pd.date_range(self.start_date,
                                      self.end_date,
                                      freq='D')]
        slider_index = (0, len(slider_dates) - 1)

        self.username = widgets.Text(
            value='',
            description='User:',
            placeholder='Your NASA Earth username ',
            disabled=False
        )
        self.password = widgets.Password(
            value='',
            placeholder='Enter password',
            description='Password:',
            disabled=False
        )
        self.credentials_button = widgets.Button(description='Set Credentials', )
        self.controls = []
        self.projection = widgets.Dropdown(
            options=['global', 'south', 'north'],
            description='Hemisphere:',
            disabled=False,
            value=properties['hemisphere']
        )
        self.dataset = widgets.SelectMultiple(
            options=['ATM', 'GLAH06', 'ILVIS2'],
            value=['ATM'],
            rows=4,
            description='Datasets',
            disabled=False
        )
        self.itrf = widgets.Dropdown(
            options=[None, 'ITRF2000', 'ITRF2008', 'ITRF2014'],
            disabled=False,
            description='ITRF:',
            layout={'width': 'max-content',
                    'display': 'flex',
                    'description_width': 'initial'}
        )
        self.epoch = widgets.Text(
            value='',
            description='Epoch:',
            placeholder='i.e. 2.1',
            disabled=False
        )
        self.is2 = widgets.Text(
            value='',
            description='IceSat 2:',
            placeholder='i.e. ATL06',
            disabled=False
        )
        self.dates_range = widgets.SelectionRangeSlider(
            options=slider_dates,
            index=slider_index,
            continuous_update=False,
            description='Date Range',
            orientation='horizontal',
            layout={'width': '100%'})

        self.granule_count = widgets.Button(description="Get Granule Count", )
        self.selection_controls = widgets.VBox([self.projection,
                                                self.dataset,
                                                self.is2,
                                                self.itrf,
                                                self.epoch,
                                                self.dates_range,
                                                self.granule_count])
        self.controls.append(self.selection_controls)
        self.layers_control = LayersControl(position='topright')
        self.search_control = SearchControl(
            position="topleft",
            url='https://nominatim.openstreetmap.org/search?format=json&q={s}',
            zoom=5,
            marker=place_marker
        )
        self.dc = DrawControl(
            circlemarker={},
            polyline={},
            rectangle={
                "shapeOptions": {
                    "fillColor": "#fca45d",
                    "color": "#fca45d",
                    "fillOpacity": 0.5
                }
            })
        self.file_upload = widgets.FileUpload(
            accept='.json,.geojson',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False  # True to accept multiple files upload else False
        )

        # Now we are going to link the controls to the relevant events
        self.dates_range.observe(self.dates_changed, 'value')
        self.projection.observe(self.hemisphere_change)
        self.credentials_button.on_click(self.set_credentials)
        self.granule_count.on_click(self.query_cmr)

    def hemisphere_change(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            self.display_map(self.map_output, hemisphere=self.projection.value)

    def dates_changed(self, change):
        if change['type'] == 'change' and change['name'] == 'value':
            start, end = change['new']
            self.start_date = start
            self.end_date = end
            # TODO: keep selection state
            # we filter the geopandas datafram to only display flights within the user range
            self.display_map(self.map_output)

    def set_credentials(self, event):
        if (self.username.value != '' and self.password.value != ''):
            self.credentials = {
                'username': self.username.value,
                'password': self.password.value
            }
        else:
            print('enter your NASA Earth login credentials')
            self.credentials = None
            return None

    def display_credentials(self, where):
        """
        renders the input controls to get the user's credentials
        note that theey are not enccrypted here.
        """
        if where == 'vertical':
            if not hasattr(self, 'sc'):
                self.sc = Sidecar(title='Map Widget')
            with self.sc:
                display(self.username, self.password, self.credentials_button)
        else:
            display(self.username, self.password, self.credentials_button)

    def display_controls(self, where):
        if where == 'vertical':
            if not hasattr(self, 'sc'):
                self.sc = Sidecar(title='Map Widget')
            with self.sc:
                for component in self.controls:
                    display(component)
        else:
            for component in self.controls:
                display(component)

    def display_map(self, map_output, hemisphere=None, extra_layers=True):
        """
        Will render the UI using ipyleaflet and jupyter widgets
        """
        self.map_output = map_output
        if hemisphere is None:
            projection = self.projections[self.projection.value]
        else:
            projection = self.projections[hemisphere]

        # TODO: maybe there is a way to create the map in the constructor
        # and just update its properties to see if this is faster.
        self.map = Map(center=projection['center'],
                       zoom=projection['zoom'],
                       max_zoom=projection['max_zoom'],
                       basemap=projection['base_map'],
                       crs=projection['projection'])

        self.map.add_control(self.dc)
        self.map.add_control(self.layers_control)
        self.map.add_control(self.search_control)
        # layers = self.projections[self.h.value]['layers']
        # for layer in layers:
        # self.map.add_layer(flights_north(self.start_date, self.end_date))
        # self.map.add_layer(flights_south(self.start_date, self.end_date))
        for layer in flight_layers[self.projection.value]:
            self.map.add_layer(layer(self.start_date, self.end_date))
        if extra_layers:
            for layer in custom_layers[self.projection.value]:
                self.map.add_layer(layer)
        self.map.layout.height = '600px'
        self.out.clear_output()
        if map_output == 'vertical':
            if hasattr(self, 'sc'):
                self.sc.clear_output()
            else:
                self.sc = Sidecar(title='Map Widget')
            with self.sc:
                display(self.out)
            with self.out:
                display(self.map)
                for component in self.controls:
                    display(component)

        else:
            with self.out:
                display(self.map)
            display(self.out)
