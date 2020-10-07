from datetime import datetime
import glob
import os
import numpy  as np
import xarray.plot as xplt
import matplotlib.pyplot as plt


import xarray as xr

from itslive import itslive_ui


class ITSCube:
    """
    Class to represent ITS_LIVE cube: time series of velocity pairs within a
    polygon of interest.
    """
    
    # TODO: provide parameters for the polygon of interest and OpenAPI params, 
    #       then download the data to be used for the cube construction.
    #       For now just use already pre-filtered downloaded data from 
    #       specified data directory.
    def __init__(self, data_dir):
        """
        data_dir: str
            Directory that stores velocity granules files as downloaded by ITS_LIVE OpenApi.
        """
        self.dir = data_dir
        
        # Load velocity pairs from all files in specified directory
        self.file_data = []
        for each_file in glob.glob(self.dir + os.sep + '*.nc'):
            ds = xr.open_dataset(each_file)
            self.file_data.append(ds)
            
        # Dictionary to store filtered (by polygon) velocities:
        # mid_date: velocity values
        self.velocities = {}
        
    # TODO: use polygon (not centroid and mean_offset) to filter out the values to be included into the cube.
    def create(self, centroid, mean_offset_meters = 1200):
        """
        Create velocity cube.
        
        centroid: list[2]
            Centroid for the polygon. This is a temporary parameter as polygon will be used 
            to filter out the data points from each layer. Just using itslive.py logic for now.
        mean_offset_meters: int
            Mean offset in meters (defines a region around centroid). Default is 1200.
        """
        # Dictionary that maps projection string to centroid coordinates in that projection
        # (to avoid re-calculation of centroid coordinates in different projections)        
        centroid_in_proj = {}

        # Re-set filtered velocities         
        self.velocities = {}

        for ds in self.file_data:
            if ds.UTM_Projection.spatial_epsg in centroid_in_proj:
                centroid_coords = centroid_in_proj[ds.UTM_Projection.spatial_epsg]

            else:
                proj = str(int(ds.UTM_Projection.spatial_epsg))
                centroid_coords = itslive_ui.transform_coord('4326', proj, centroid[0], centroid[1])
                centroid_in_proj[ds.UTM_Projection.spatial_epsg] = centroid_coords

            projected_lon = round(centroid_coords[0])
            projected_lat = round(centroid_coords[1])
            mid_date = datetime.strptime(ds.img_pair_info.date_center,'%Y%m%d')

            # We are going to calculate the mean value of the neighboring pixels(each is 240m) 10 x 10 window
            mask_lon = (ds.x >= projected_lon - mean_offset_meters) & (ds.x <= projected_lon + mean_offset_meters)
            mask_lat = (ds.y >= projected_lat - mean_offset_meters) & (ds.y <= projected_lat + mean_offset_meters)

            cube_v = ds.where(mask_lon & mask_lat , drop=True).v

            # For now just add middle date as an attribute
            cube_v.attrs['mid_date'] = mid_date

            # TODO: Should add a filename as its source for traceability?

            # If it's a valid velocity layer, add it to the cube.
            if np.any(cube_v.notnull()):
                # There might be multiple layers for the mid_date, use filename to detect which one to include
                # into the cube: the one in target projection.                
                self.velocities[mid_date] = cube_v
                
        # Construct xarray to hold layers in date order
        # cube = xr.DataSet({"time": datetime.datetime(2000, 1, 1)})

    def plot_layers(self):
        """
        Plot cube layers in date order.
        """
        num_granules = len(self.velocities)
        
        # TODO: should split images into multiple rows if there are many of them. 
        #       This works fine for 7 layers.
        fig, axes = plt.subplots(ncols=num_granules, nrows=1, figsize=(num_granules*5, 5))
        for each_index, each_date in enumerate(sorted(self.velocities.keys())):
            self.velocities[each_date].plot(ax=axes[each_index])
            axes[each_index].title.set_text(str(self.velocities[each_date].attrs['mid_date']))
            
        plt.tight_layout()
        plt.draw()
    
