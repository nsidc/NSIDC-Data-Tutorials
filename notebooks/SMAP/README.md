## SMAP Python Notebooks

### Summary

In this set of three tutorials we demonstrate how to search for, download and plot SMAP data. Tutorial 1 demonstrates how to search for and download SMAP data using the `earthaccess` library. The second tutorial demonstrates how to read in and plot the data downloaded in Tutorial 1. And Tutorial 3 provides information on the surface quality and retrieval quality flags. 

We use the [SMAP L3 Radiometer Global Daily 36 km EASE-Grid Soil Moisture, Version 8](https://nsidc.org/data/SPL3SMP/versions/8) data set as an example.

**NOTE** these notebooks are an updated version of the notebooks orginially published in this [repo](https://github.com/nsidc/smap_python_notebooks/tree/main). The notebooks are based on notebooks originally provided to NSIDC by Adam Purdy. Jennifer Roebuck of NSIDC applied the following updates:
* Used `earthaccess` instead of `requests` for authentication, searching for and downloading the data. This reduced the code to just a few lines.
* Used a more recent version of SPL3SMP (version 8).
* Replaced the use of `Basemap` with `cartopy`. 
* Updated the surface quality flag names to reflect the ones used in the latest version. 
* Minor text edits to provide additional information where necessary.
* Moved the tutorials to the standard NSIDC tutorials template. 

### Set up

To run the notebook provided in this folder, please see the [NSIDC-Data-Tutorials repository readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions on several ways (using Binder, Docker, or Conda) to do this.

### Key Learning Objectives

1. Use the `earthaccess` library to search for and download SMAP data.
2. Use the `h5py` library to read in the HDF5 files and plot the variables on a map using `cartopy` and `matplotlib`.
3. Understand the surface quality and retrieval quality flag options.
