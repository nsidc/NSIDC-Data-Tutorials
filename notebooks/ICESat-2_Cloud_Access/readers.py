## Based on the READ function form Younghyun Koo for the sea ice tutorial at the IS2 hackweek

'''
Code to read s3 file without earthaccess open

from itertools import chain
for year, granules in atl10.items():
    
    data_links = list(
        chain.from_iterable(
            granule.data_links(access="direct") for granule in granules
            )
    )
data_links[0]

from readers import get_credentials

file = data_links[0]

h5coro.config(errorChecking=True, verbose=False, enableAttributes=False)

h5obj = h5coro.H5Coro(file.replace("s3://",""), s3driver.S3Driver, credentials=get_credentials(file))

h5obj.readDatasets(["gt1l/freeboard_segment/beam_fb_height"], block=True)

for dataset in h5obj:
    print(dataset)
'''

from itertools import product
from pqdm.threads import pqdm

from h5coro import h5coro, s3driver

import geopandas as gpd
import pandas as pd
import numpy as np


GPS_EPOCH = pd.to_datetime('1980-01-06 00:00:00')

def get_strong_beams(f):
    """Returns ground track for strong beams based on IS2 orientation"""
    orient  = f['orbit_info/sc_orient'][0]

    if orient == 0:
        return [f"gt{i}l" for i in [1, 2, 3]]
    elif orient == 1:
        return [f"gt{i}r" for i in [1, 2, 3]]
    else:
        raise KeyError("Spacecraft orientation neither forward nor backward")


def get_credentials(file):
    """Returns credentials dict with keys expected by h5coro
    
    TODO: could add as option for earthaccess
    """
    return {
        "aws_access_key_id": file.s3.storage_options["key"],
        "aws_secret_access_key": file.s3.storage_options["secret"],
        "aws_session_token": file.s3.storage_options["token"]
    }
    
    
def read_atl10_local(files, executors):
    """Returns a consolidated GeoPandas dataframe for a set of ATL10 file pointers.
    
    Parameters:
        files (list[S3FSFile]): list of authenticated fsspec file references to ATL10 on S3 (via earthaccess)
        executors (int): number of threads
    
    """
    def read_atl10(file):
        """Reads datasets required for creating gridded freeboard from a single ATL10 file
        
        file: an authenticated fsspec file reference on S3 (returned by earthaccess)
        
        returns: a list of geopandas dataframes
        """
        
        # Open file object
        f = h5coro.H5Coro(file.info()["name"], s3driver.S3Driver, credentials=get_credentials(file))
        
        # Get strong beams based on orientation
        ancillary_datasets = ["orbit_info/sc_orient", "ancillary_data/atlas_sdp_gps_epoch"]
        f.readDatasets(datasets=ancillary_datasets, block=True)
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
        f.readDatasets(datasets=ds_list, block=True)
        
        # Create a list of geopandas.DataFrames containing beams
        tracks = []
        for beam in strong_beams:
            ds = {dataset.split("/")[-1]: f[dataset][:] for dataset in ds_list if dataset.startswith(beam)}
            
            # Convert delta_time to datetime
            ds["delta_time"] = GPS_EPOCH + pd.to_timedelta(ds["delta_time"]+atlas_sdp_gps_epoch, unit='s')

            # Add beam identifier
            ds["beam"] = beam
            
            # Set fill values to NaN - assume 100 m as threshold
            ds["beam_fb_height"] = np.where(ds["beam_fb_height"] > 100, np.nan, ds["beam_fb_height"])
            
            geometry = gpd.points_from_xy(ds["longitude"], ds["latitude"])
            del ds["longitude"]
            del ds["latitude"]
            
            gdf = gpd.GeoDataFrame(ds, geometry=geometry, crs="EPSG:4326")
            gdf.dropna(axis=0, inplace=True)
            tracks.append(gdf)

#             gc.collect()
        return tracks
    
    df = pqdm(files, read_atl10, n_jobs=executors)
    combined = pd.concat([t[0] for t in df if type(t) is list])
    
    return combined