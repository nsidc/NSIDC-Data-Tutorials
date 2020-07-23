import pandas as pd
import ipywidgets as widgets
import itertools
from ipyleaflet import projections, basemaps, DrawControl

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
        'center': (0,0)
    },
    'north': {
        'base_map': basemaps.NASAGIBS.BlueMarble3413,
        'projection': north_3413,
        'center': (90,0)
    },
    'south': {
        'base_map': basemaps.NASAGIBS.BlueMarble3031,
        'projection': south_3031,
        'center': (-90,0)
    }
}

def nasa_username_control(properties):
    control = widgets.Text(
        value='',
        description='User:',
        placeholder='Your NASA Earth username ',
        disabled=False
    )
    return control



def nasa_password_control(properties):
    control = widgets.Password(
        value='',
        placeholder='Enter password',
        description='Password:',
        disabled=False
    )
    return control

def nasa_set_credentials_control(properties):
    set_control =  widgets.Button(description="Verify Credentials", )
    return set_control


def datasets_control(properties):
    dataset = widgets.SelectMultiple(
        options=['ATM', 'GLAH06', 'ILVIS2'],
        value=['ATM'],
        rows=4,
        description='Datasets',
        disabled=False
    )
    return dataset

def dates_slider_control(properties):
    slider_dates = [(date.strftime(' %Y-%m-%d '), date) for date in
                    pd.date_range(properties['start_date'],
                                    properties['end_date'],
                                    freq='D')]
    slider_index = (0, len(slider_dates)-1)
    date_slider_control = widgets.SelectionRangeSlider(
                options=slider_dates,
                index=slider_index,
                description='Date Range',
                orientation='horizontal',
                layout={'width': '100%'})
    return date_slider_control



def draw_control(properties):
    control = DrawControl(circlemarker={},
                    polyline={},
                    rectangle = {
                        "shapeOptions": {
                        "fillColor": "#fca45d",
                            "color": "#fca45d",
                            "fillOpacity": 0.5
                        }
    })
    return control


def epoch_control(properties):
    epoch = widgets.Text(
        value='',
        placeholder='i.e. 2.1',
        disabled=False
    )
    return epoch


def file_control(properties):
    control = widgets.FileUpload(
        accept='.json,.geojson',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
        multiple=False  # True to accept multiple files upload else False
    )
    return control


def itrf_control(properties):
    itrf = widgets.Dropdown(
        options= [None, 'ITRF2000', 'ITRF2008', 'ITRF2014'],
        disabled=False,
        layout={'width': 'max-content',
                'display': 'flex',
                'description_width': 'initial'}
    )
    return itrf


def projection_control(properties):
    control = widgets.Dropdown(
        options=['global', 'south', 'north'],
        description='Hemisphere:',
        disabled=False,
        value=properties['hemisphere']
    )
    return control


def cmr_counts_control(properties):
    granule_count =  widgets.Button(description="Get Granule Count", )
    return granule_count


def format_polygon(geometry):
    coords = [[str(float("{:.4f}".format(coord[0]))),str(float("{:.4f}".format(coord[1])))] for coord in geometry['coordinates'][0]]
    coords = list(itertools.chain.from_iterable(coords))
    polygonstr = ','.join(coords)
    return polygonstr

