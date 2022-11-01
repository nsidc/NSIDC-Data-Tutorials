from datetime import datetime, timedelta
from pathlib import PurePosixPath

import geopandas as gpd
import h5py
import numpy as np
import pandas as pd


class IceFlowProcessing:
    @staticmethod
    def to_geopandas(filename):
        with h5py.File(filename, "r") as h5:
            if "d_elev" in list(h5.keys()):
                # GLAS dataframe
                df_data = {
                    "latitude": h5["d_lat"],
                    "longitude": h5["d_lon"],
                    "elevation": h5["d_elev"],
                    "time": pd.to_datetime(h5["utc_datetime"][:].astype(str)),
                }
            if "elevation" in list(h5.keys()):
                # ATM data
                df_data = {
                    "latitude": h5["latitude"],
                    "longitude": h5["longitude"],
                    "elevation": h5["elevation"],
                    "time": pd.to_datetime(h5["utc_datetime"][:].astype(str)),
                }
            if "gt1l" in list(h5.keys()):  # ICESat-2
                # Get dataproduct name
                dataproduct = h5.attrs["identifier_product_type"].decode()
                # Set variables for each ATL* product
                VARIABLES = {
                    "ATL06": [
                        "/gt1l/land_ice_segments/delta_time",
                        "/gt1l/land_ice_segments/h_li",
                        "/gt1l/land_ice_segments/latitude",
                        "/gt1l/land_ice_segments/longitude",
                        "/gt1r/land_ice_segments/delta_time",
                        "/gt1r/land_ice_segments/h_li",
                        "/gt1r/land_ice_segments/latitude",
                        "/gt1r/land_ice_segments/longitude",
                        "/gt2l/land_ice_segments/delta_time",
                        "/gt2l/land_ice_segments/h_li",
                        "/gt2l/land_ice_segments/latitude",
                        "/gt2l/land_ice_segments/longitude",
                        "/gt2r/land_ice_segments/delta_time",
                        "/gt2r/land_ice_segments/h_li",
                        "/gt2r/land_ice_segments/latitude",
                        "/gt2r/land_ice_segments/longitude",
                        "/gt3l/land_ice_segments/delta_time",
                        "/gt3l/land_ice_segments/h_li",
                        "/gt3l/land_ice_segments/latitude",
                        "/gt3l/land_ice_segments/longitude",
                        "/gt3r/land_ice_segments/delta_time",
                        "/gt3r/land_ice_segments/h_li",
                        "/gt3r/land_ice_segments/latitude",
                        "/gt3r/land_ice_segments/longitude",
                    ],
                }
                # Convert variable paths to 'Path' objects for easy manipulation
                variables = [PurePosixPath(v) for v in VARIABLES[dataproduct]]
                # Get set of beams to extract individially as dataframes combining in the end
                beams = {list(v.parents)[-2].name for v in variables}
                dfs = []
                for beam in beams:
                    data_dict = {}
                    beam_variables = [v for v in variables if beam in str(v)]
                    for variable in beam_variables:
                        # Use variable 'name' as column name. Beam will be specified in 'beam' column
                        column = variable.name
                        variable = str(variable)
                        try:
                            values = h5[variable][:]
                            # Convert invalid data to np.nan (only for float columns)
                            if "float" in str(values.dtype):
                                if "valid_min" in h5[variable].attrs:
                                    values[
                                        values < h5[variable].attrs["valid_min"]
                                    ] = np.nan
                                if "valid_max" in h5[variable].attrs:
                                    values[
                                        values > h5[variable].attrs["valid_max"]
                                    ] = np.nan
                                if "_FillValue" in h5[variable].attrs:
                                    values[
                                        values == h5[variable].attrs["_FillValue"]
                                    ] = np.nan

                            data_dict[column] = values
                        except KeyError:
                            print(f"Variable {variable} not found in {filename}.")

                    df_data = pd.DataFrame.from_dict(data_dict)
                    dfs.append(df_data)

                df_data = pd.concat(dfs, sort=True)
                # Add filename column for book-keeping and reset index
                df_data = df_data.reset_index(drop=True)
                EPOCH = datetime(2018, 1, 1, 0, 0, 0)
                df_data["delta_time"] = df_data["delta_time"].map(
                    lambda x: EPOCH + timedelta(seconds=x)
                )
                df_data.rename(
                    columns={"delta_time": "time", "h_li": "elevation"}, inplace=True
                )
                df_data = df_data[["time", "latitude", "longitude", "elevation"]]

            df = pd.DataFrame(data=df_data)

        geopandas_df = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(
                df["longitude"], df["latitude"], crs="epsg:4326"
            ),
        )
        geopandas_df = geopandas_df.set_index("time")
        return geopandas_df

    @staticmethod
    def get_common_df(filename):
        """
        Returns a minimal pandas dataframe for the different IceFlow datasets with the following keys
        latitude,longitude,elevation,time.
        Params: hdf_f, an h5py file object
        """
        with h5py.File(filename, "r") as h5:
            if "d_elev" in list(h5.keys()):
                # GLAS dataframe
                df_data = {
                    "latitude": h5["d_lat"],
                    "longitude": h5["d_lon"],
                    "elevation": h5["d_elev"],
                    "time": pd.to_datetime(h5["utc_datetime"]),
                }
            if "elevation" in list(h5.keys()):
                # ATM data
                df_data = {
                    "latitude": h5["latitude"],
                    "longitude": h5["longitude"],
                    "elevation": h5["elevation"],
                    "time": pd.to_datetime(h5["utc_datetime"]),
                }
            df = pd.DataFrame(data=df_data)
        return df

    @staticmethod
    def get_common_dictionary(dataset):
        """
        Returns a simple dictionary with key values for different datasets
        """
        if dataset == "GLAS":
            data_dict = {
                "latitude": "d_lat",
                "longitude": "d_lon",
                "elevation": "d_elev",
                "time": "utc_datetime",
            }
            return data_dict
        if dataset == "ATM":
            # ATM data
            data_dict = {
                "latitude": "latitude",
                "longitude": "longitude",
                "elevation": "elevation",
                "time": "utc_datetime",
            }
            return data_dict
