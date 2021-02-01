import h5py
import pandas as pd
import geopandas as gpd


class IceFlowProcessing:

    @staticmethod
    def to_geopandas(filename):
        with h5py.File(filename, 'r') as h5:
            if 'd_elev' in list(h5.keys()):
                # GLAS dataframe
                df_data = {
                    'latitude': h5['d_lat'],
                    'longitude': h5['d_lon'],
                    'elevation': h5['d_elev'],
                    'time': pd.to_datetime(h5['utc_datetime'])
                }
            if 'elevation' in list(h5.keys()):
                # ATM data
                df_data = {
                    'latitude': h5['latitude'],
                    'longitude': h5['longitude'],
                    'elevation': h5['elevation'],
                    'time': pd.to_datetime(h5['utc_datetime'])
                }
            df = pd.DataFrame(data=df_data)

        geopandas_df = gpd.GeoDataFrame(df,
                                        geometry=gpd.points_from_xy(df['longitude'],
                                                                    df['latitude'],
                                                                    crs='epsg:4326'))
        return geopandas_df

    @staticmethod
    def get_common_df(filename):
        """
        Returns a minimal pandas dataframe for the different IceFlow datasets with the following keys
        latitude,longitude,elevation,time.
        Params: hdf_f, an h5py file object
        """
        with h5py.File(filename, 'r') as h5:
            if 'd_elev' in list(h5.keys()):
                # GLAS dataframe
                df_data = {
                    'latitude': h5['d_lat'],
                    'longitude': h5['d_lon'],
                    'elevation': h5['d_elev'],
                    'time': pd.to_datetime(h5['utc_datetime'])
                }
            if 'elevation' in list(h5.keys()):
                # ATM data
                df_data = {
                    'latitude': h5['latitude'],
                    'longitude': h5['longitude'],
                    'elevation': h5['elevation'],
                    'time': pd.to_datetime(h5['utc_datetime'])
                }
            df = pd.DataFrame(data=df_data)
        return df

    @staticmethod
    def get_common_dictionary(dataset):
        """
        Returns a simple dictionary with key values for different datasets
        """
        if dataset == 'GLAS':
            data_dict = {
                'latitude': 'd_lat',
                'longitude': 'd_lon',
                'elevation': 'd_elev',
                'time': 'utc_datetime'
            }
            return data_dict
        if dataset == 'ATM':
            # ATM data
            data_dict = {
                'latitude': 'latitude',
                'longitude': 'longitude',
                'elevation': 'elevation',
                'time': 'utc_datetime'
            }
            return data_dict
