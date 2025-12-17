## SMAP Python Notebooks

### Summary

This set of three tutorials demonstrates how to search for, download and plot SMAP data using `xarray` and how to make the SMAP data into a georeferenced dataset. 

We use the [SMAP L3 Radiometer Global Daily 36 km EASE-Grid Soil Moisture, Version 9](https://nsidc.org/data/SPL3SMP/versions/9) data set as an example.

All notebooks are self contained, so there is no particular order to run them.  However, [working_with_smap_data_in_xarray](notebooks/SMAP/working_with_smap_in_xarray.ipynb) provides the most basic introduction.

[working_with_smap_data_in_xarray](notebooks/SMAP/working_with_smap_in_xarray.ipynb) demonstrates how to search for and download SMAP data using `earthaccess`, and how to load a single group into an `xarray.Dataset` using `open_dataset`.  It also shows how to add informative dimension names and geospatial coordinates to the dataset so that the data variables can be plotted and analyzed using the powerful `xarray` methods.

[working_with_smap_as_datatree](notebooks/SMAP/working_with_smap_as_datatree.ipynb) demonstrates how to load the full SMAP datafile as an `xarray.Datatree`.  It also shows how to load a time series of SMAP files.

[create_geospatial_dataset_in_xarray](notebooks/SMAP/create_geospatial_dataset_in_xarray.ipynb) is essentially the same workflow as `working_with_smap_data_in_xarray` but provides more detail and the rationale behind the modifications.

**NOTE** these notebooks are an updated version of the notebooks orginially published in this [repo](https://github.com/nsidc/smap_python_notebooks/tree/main). The notebooks are based on notebooks originally provided to NSIDC by Adam Purdy. Jennifer Roebuck of NSIDC applied the following updates:
* Used `earthaccess` instead of `requests` for authentication, searching for and downloading the data. This reduced the code to just a few lines.
* Used a more recent version of SPL3SMP (version 8).
* Replaced the use of `Basemap` with `cartopy`. 
* Updated the surface quality flag names to reflect the ones used in the latest version. 
* Minor text edits to provide additional information where necessary.
* Moved the tutorials to the standard NSIDC tutorials template. 

The notebooks were modified by Andy Barrett of NSIDC to take advantage of `xarray.DataTree` and modern tooling.  This involved a rewrite of the notebooks and using version 9 of SPL3SMP.

### Set up

To run the notebook provided in this folder, please see the [NSIDC-Data-Tutorials repository readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions on several ways (using Binder, Docker, or Conda) to do this.

### Key Learning Objectives

1. Use the `earthaccess` library to search for and download SMAP data.
2. Use the `xarray` library to read in the HDF5 files and plot the variables on a map using `xarray` plotting methods and `cartopy`.
