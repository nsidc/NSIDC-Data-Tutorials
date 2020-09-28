import pandas as pd


class IceFlowProcessing:

    @staticmethod
    def get_common_df(hdf_f):
        """
        Returns a minimal pandas dataframe for the different IceFlow datasets with the following keys
        latitude,longitude,elevation,time.
        Params: hdf_f, an h5py file object
        """
        if 'd_elev' in list(hdf_f.keys()):
            # GLAS dataframe
            df_data = {
                'latitude': hdf_f['d_lat'],
                'longitude': hdf_f['d_lon'],
                'elevation': hdf_f['d_elev'],
                'time': pd.to_datetime(hdf_f['utc_datetime'])
            }
            return pd.DataFrame(data=df_data)
        if 'elevation' in list(hdf_f.keys()):
            # ATM data
            df_data = {
                'latitude': hdf_f['latitude'],
                'longitude': hdf_f['longitude'],
                'elevation': hdf_f['elevation'],
                'time': pd.to_datetime(hdf_f['utc_datetime'])
            }
            return pd.DataFrame(data=df_data)

    @staticmethod
    def get_common_dictionary(dataset):
        """
        Returns a simple dictionary with key values for different datasets
        """
        if dataset == 'GLASS':
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
