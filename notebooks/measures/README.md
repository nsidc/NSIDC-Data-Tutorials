## Search, Download and Plot multiple GeoTIFFs

### Summary 
In this tutorial we demonstrate how to programmatically access and download GeoTIFF files from the NSIDC DAAC data to your local computer. We then walk through the steps for cropping and resampling one GeoTIFF based on the extent and pixel size of another GeoTIFF, with the end goal of plotting one on top of the other. 

We use two data sets from the NASA [MEaSUREs](https://nsidc.org/data/measures) (Making Earth System data records for Use in Research Environments) program as an example:

* [MEaSUREs Greenland Ice Mapping Project (GrIMP) Digital Elevation Model from GeoEye and WorldView Imagery, Version 2 (NSIDC-0715)](https://nsidc.org/data/nsidc-0715/versions/2)
* [MEaSUREs Greenland Ice Velocity: Selected Glacier Site Velocity Maps from InSAR, Version 4 (NSIDC-0481)](https://nsidc.org/data/nsidc-0481/versions/4)


### Set up

To run the notebook provided in this folder, please see the [NSIDC-Data-Tutorials repository readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions on several ways (using Binder, Docker, or Conda) to do this.

### Key Learning Objectives 

1. Use the `earthaccess` library for authentication and to programmatically search for and download NSIDC DAAC data that meet specified spatial and temporal requirements. 
2. Use the `gdal` and `osr` modules from the `osgeo` package to crop and resample one GeoTIFF based on the extent and pixel size of another GeoTIFF.
3. Use `rasterio`, `numpy` and `matplotlib` libraries to overlay one GeoTIFF on top of another.
