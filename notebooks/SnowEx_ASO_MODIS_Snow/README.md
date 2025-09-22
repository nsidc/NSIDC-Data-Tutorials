# Snow Depth and Snow Cover Data Exploration 

## Overview

This tutorial demonstrates how to access and compare coincident snow data from in-situ Ground Pentrating Radar (GPR) measurements, and airborne and satellite platforms from NASA's SnowEx, ASO, and MODIS data sets. All data are available from the NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC). 

## What you will learn in this tutorial

In this tutorial you will learn:

1. what snow data and information is available from NSIDC and the resources available to search and access this data;
2. how to search and access spatiotemporally coincident data across in-situ, airborne, and satellite observations.
3. how to read SnowEx GPR data into a Geopandas GeoDataFrame;
4. how to read ASO snow depth data from GeoTIFF files using xarray;
5. how to read MODIS Snow Cover data from HDF-EOS files using xarray;
6. how to subset gridded data using a bounding box;
5. how to extract and visualize raster values at point locations;
6. how to save output as shapefile.

## Setup

We recommend creating a virtual environment to run this notebook.  This can be with `mamba` or `conda`.  We recommend `mamba`.

```
mamba env update -f environment/environment.yml
```

This will create an environment called `nsidc-tutorials-snowex`. You can activate the environment with the command:

```
mamba activate nsidc-tutorials-snowex
```

You will now have a virtual environment with all the required packages.  You can start a `jupyter lab` with

```
jupyter lab
```
