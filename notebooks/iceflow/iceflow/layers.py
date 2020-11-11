from ipyleaflet import TileLayer, GeoJSON, projections, basemaps
import pandas as pd
import geopandas
import json

greenland_velocities = 'https://gibs.earthdata.nasa.gov/wmts/epsg3413/best/' + \
                       'MEaSUREs_Ice_Velocity_Greenland/default/2008-12-01/500m/{z}/{y}/{x}.png'

itslive_layer = TileLayer(opacity=1.0,
                          name='Ice Velocities',
                          url=greenland_velocities,
                          zoom=1,
                          min_zoom=1,
                          max_zoom=4)

df_north = geopandas.read_file('./iceflow/files/ib_north.json')
df_north['date'] = pd.to_datetime(df_north['timestamp'])

df_south = geopandas.read_file('./iceflow/files/ib_south.json')
df_south['date'] = pd.to_datetime(df_south['timestamp'])


def filter_layer(df, name, start, end):
    if start is None and end is None:
        return df[['timestamp', 'geometry']].to_json()
    filtered_frame = df[df.date.between(start, end)][['timestamp', 'geometry']].to_json()
    geo_layer = GeoJSON(
        name=name,
        data=json.loads(filtered_frame),
        style={
            'opacity': 0.5, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 0.5
        }
    )
    return geo_layer


def flights_south(start, end):
    layer = filter_layer(df_south, 'IceBridge South', start, end)
    return layer


def flights_north(start, end):
    layer = filter_layer(df_north, 'IceBridge North', start, end)
    return layer


flight_layers = {
    'north': [flights_north],
    'south': [flights_south],
    'global': [flights_south, flights_north]
}

custom_layers = {
    'north': [itslive_layer],
    'south': [],
    'global': []
}

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

widget_projections = {
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
