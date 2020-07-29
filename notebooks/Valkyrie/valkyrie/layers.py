from ipyleaflet import TileLayer, GeoJSON
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

df_north = geopandas.read_file('./valkyrie/files/ib_north.json')
df_north['date'] = pd.to_datetime(df_north['timestamp'])

df_south = geopandas.read_file('./valkyrie/files/ib_south.json')
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
