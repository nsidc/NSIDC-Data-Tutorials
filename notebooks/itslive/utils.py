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


def pixels_control(properties):
    valid_percentages = [str(p) for p in range(0,100,10)]
    valid_percentages[0] = 1
    pixels = widgets.Dropdown(
        options=valid_percentages,
        disabled=False,
        layout={'width': 'max-content',
                'display': 'flex',
                'description_width': 'initial'}
    )
    return pixels

def time_delta_control(properties):
    time_delta = widgets.Dropdown(
        options=['any', '7','30','90','120', '365'],
        disabled=False,
        layout={'width': 'max-content',
                'display': 'flex',
                'description_width': 'initial'}
    )
    return time_delta


def projection_control(properties):
    control = widgets.Dropdown(
        options=['global', 'south', 'north'],
        description='Hemisphere:',
        disabled=False,
        value=properties['hemisphere']
    )
    return control

def coverage_control():
    granule_count =  widgets.Button(description="Get Granule Count", )
    granule_count.on_click(query_cmr)




def format_polygon(geometry):
    coords = [[str(float("{:.4f}".format(coord[0]))),str(float("{:.4f}".format(coord[1])))] for coord in geometry['coordinates'][0]]
    coords = list(itertools.chain.from_iterable(coords))
    polygonstr = ','.join(coords)
    return polygonstr




def query_(b):
    granules = []
    datasets_cmr = []
    datasets_valkyrie = []
    d1 = date_range_slider.value[0].date()
    d2 = date_range_slider.value[1].date()
    if dc.last_draw['geometry'] is None:
        print('You need to select an area using the box tool')
        return None
    coords = [list(coord) for coord in bounding_box(dc.last_draw['geometry']['coordinates'][0])]
    bbox = (coords[0][0],coords[0][1],coords[1][0],coords[1][1])
    if 'ATM' in dataset.value:
        datasets_cmr.extend([{'name':'ILATM1B'},{'name':'BLATM1B'}])
        datasets_valkyrie.append('ATM1B')
    if 'GLAH06' in dataset.value:
        datasets_cmr.append({'name':'GLAH06'})
        datasets_valkyrie.append('GLAH06')
    if 'ILVIS2' in dataset.value:
        datasets_cmr.append({'name': 'ILVIS2', 'version': '002'})
        datasets_valkyrie.append('ILVIS2')

    for d in datasets_cmr:
        cmr_api = GranuleQuery()
        g = cmr_api.parameters(
            short_name=d['name'],
            temporal=(d1,d2),
            bounding_box = bbox).hits()
        granules.append({d['name']: g})
    if b is not None:
        print(granules)
    return granules

# granule_count =  widgets.Button(description="Get Granule Count", )
# granule_count.on_click(query_cmr)


def post_orders(params):
    responses = []
    datasets_valkyrie = []
    if 'ATM' in dataset.value:
        datasets_valkyrie.append('ATM1B')
    if 'GLAH06' in dataset.value:
        datasets_valkyrie.append('GLAH06')
    if 'ILVIS2' in dataset.value:
        datasets_valkyrie.append('ILVIS2')
    for d in datasets_valkyrie:
        base_url = f'http://staging.valkyrie-vm.apps.nsidc.org/1.0/{d}'
        response = requests.post(base_url, params=params)
        # now we are going to return the response from Valkyrie
        responses.append({d: response.json()})
    return responses

