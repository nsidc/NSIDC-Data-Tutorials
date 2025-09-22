#!/usr/bin/env python

#import coiled

import geopandas as gpd
import numpy as np
import pandas as pd
from rich import print as rprint
from itertools import product
from pqdm.threads import pqdm


import earthaccess
from h5coro import s3driver, webdriver
import h5coro




def get_strong_beams(f):
    """Returns ground track for strong beams based on IS2 orientation"""
    orient  = f['orbit_info/sc_orient'][0]

    if orient == 0:
        return [f"gt{i}l" for i in [1, 2, 3]]
    elif orient == 1:
        return [f"gt{i}r" for i in [1, 2, 3]]
    else:
        raise KeyError("Spacecraft orientation neither forward nor backward")






def read_atl10(files, bounding_box=None, executors=4, environment="local", credentials=None):
    """Returns a consolidated GeoPandas dataframe for a set of ATL10 file pointers.

    Parameters:
        files (list[S3FSFile]): list of authenticated fsspec file references to ATL10 on S3 (via earthaccess)
        executors (int): number of threads

    """
    if environment == "local":
        driver = webdriver.HTTPDriver
    else:
        driver = s3driver.S3Driver

    GPS_EPOCH = pd.to_datetime('1980-01-06 00:00:00')

    def read_h5coro(file):
        """Reads datasets required for creating gridded freeboard from a single ATL10 file

        file: an authenticated fsspec file reference on S3 (returned by earthaccess)

        returns: a list of geopandas dataframes
        """
        # Open file object
        h5 = h5coro.H5Coro(file, driver, credentials=credentials)

        # Get strong beams based on orientation
        ancillary_datasets = ["orbit_info/sc_orient", "ancillary_data/atlas_sdp_gps_epoch"]
        f = h5.readDatasets(datasets=ancillary_datasets, block=True)
        strong_beams = get_strong_beams(f)
        atlas_sdp_gps_epoch = f["ancillary_data/atlas_sdp_gps_epoch"][:]

        # Create list of datasets to load
        datasets = ["freeboard_segment/latitude",
                    "freeboard_segment/longitude",
                    "freeboard_segment/delta_time",
                    "freeboard_segment/seg_dist_x",
                    "freeboard_segment/heights/height_segment_length_seg",
                    "freeboard_segment/beam_fb_height",
                    "freeboard_segment/heights/height_segment_type"]
        ds_list = ["/".join(p) for p in list(product(strong_beams, datasets))]
        # Load datasets
        f = h5.readDatasets(datasets=ds_list, block=True)
        # rprint(f["gt2l/freeboard_segment/latitude"], type(f["gt2l/freeboard_segment/latitude"]))

        # Create a list of geopandas.DataFrames containing beams
        tracks = []
        for beam in strong_beams:
            ds = {dataset.split("/")[-1]: f[dataset][:] for dataset in ds_list if dataset.startswith(beam)}

            # Convert delta_time to datetime
            ds["delta_time"] = GPS_EPOCH + pd.to_timedelta(ds["delta_time"]+atlas_sdp_gps_epoch, unit='s')
            # we don't need nanoseconds to grid daily let alone weekly
            ds["delta_time"] = ds["delta_time"].astype('datetime64[s]')

            # Add beam identifier
            ds["beam"] = beam

            # Set fill values to NaN - assume 100 m as threshold
            ds["beam_fb_height"] = np.where(ds["beam_fb_height"] > 100, np.nan, ds["beam_fb_height"])

            geometry = gpd.points_from_xy(ds["longitude"], ds["latitude"])
            del ds["longitude"]
            del ds["latitude"]

            gdf = gpd.GeoDataFrame(ds, geometry=geometry, crs="EPSG:4326")
            gdf.dropna(axis=0, inplace=True)
            if bounding_box is not None:
                bbox = [float(coord) for coord in bounding_box.split(",")]
                gdf = gdf.cx[bbox[0]:bbox[2],bbox[1]:bbox[3]]
            tracks.append(gdf)

        df = pd.concat(tracks)
        return df

    dfs = pqdm(files, read_h5coro, n_jobs=executors)
    combined = pd.concat(dfs)

    return combined


