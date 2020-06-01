import ipywidgets as widgets
import pandas as pd
from datetime import datetime,date
from ipyleaflet import projections, basemaps

start_date = datetime(1993, 1, 1)
end_date = datetime(2019, 12, 31)

dates = pd.date_range(start_date, end_date, freq='D')
options = [(date.strftime(' %Y-%m-%d '), date) for date in dates]
index = (0, len(options)-1)

date_range_slider = widgets.SelectionRangeSlider(
    options=options,
    index=index,
    description='Date Range',
    orientation='horizontal',
    layout={'width': '500px'}
)

dataset = widgets.Dropdown(
    options=['ATM1B', 'GLAH06', 'ILVIS2'],
    description='Dataset:',
    disabled=False,
)

hemisphere = {
    'north': {
        'base_map': basemaps.NASAGIBS.BlueMarble3413,
        'projection': projections.EPSG3413,
        'center': (90,0)
    },
    'south': {
        'base_map': basemaps.NASAGIBS.BlueMarble3031,
        'projection': projections.EPSG3031,
        'center': (-90,0)
    }
}

ITRF = widgets.Dropdown(
    options=['', 'ITRF2000', 'ITRF2008', 'ITRF2014'],
    description='ITRF:',
    disabled=False,
)

# def print_date_range(date_range):
#     print(date_range)

# widgets.interact(
#     print_date_range,
#     date_range=date_range_slider
# );

def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

def build_params(dc):
    if dc.last_draw['geometry'] is None:
        print('You need to select an area using the box tool')
        return None
    coords = [list(coord) for coord in bounding_box(dc.last_draw['geometry']['coordinates'][0])]
    bbox = f'{coords[0][0]},{coords[0][1]},{coords[1][0]},{coords[1][1]}'
    d1 = date_range_slider.value[0].date()
    d2 = date_range_slider.value[1].date()
    if (d2-d1).days > 180:
        print('Remember this is a tutorial, if you want more than a year of data please contact NSIDC support')
        print('...Adjust the time range slider and try again!')
        return None
    start = d1.strftime('%Y-%m-%d')
    end = d2.strftime('%Y-%m-%d')

    params = {
        'time_range': f'{start},{end}',
        'bbox': bbox
    }
    if ITRF.value != '' :
        params['itrf'] = ITRF.value
    return params
