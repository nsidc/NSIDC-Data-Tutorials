# IceFlow Point Cloud Data Access

> [!CAUTION]
> The IceFlow notebooks and supporting code have some known problems and users
> should exercise caution. It is likely that users will run into errors while
> interacting with the notebooks. Requests for ITRF transformations are not
> currently working as expected. We recommend users look at the `corrections`
> notebook for information about how to apply ITRF transformations to data
> themselves. IceFlow is currently under maintenence, and we hope to resolve
> some of these issues soon.

## Summary

The IceFlow python library simplifies accessing and combining data from several of NASA's cryospheric altimetry missions, including ICESat/GLAS, Operation IceBridge, and ICESat-2. In particular, IceFlow harmonizes the various file formats and georeferencing parameters across several of the missions' data sets, allowing you to analyze data across the multi-decadal time series.

The contents of the IceFlow folder include the IceFlow library itself, along with several Jupyter Notebooks that provide data access and harmonization using IceFlow. If you are new to IceFlow, we recommend starting at [0_introduction.ipynb](https://github.com/nsidc/NSIDC-Data-Tutorials/blob/main/notebooks/iceflow/0_introduction.ipynb), which provides a descriptive background on the data, as well as both map widget-based and programmatic-based options for accessing data from IceFlow.

## Setup

To run the notebooks provided in this folder, please see the [NSIDC-Data-Tutorials repository readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions on several ways (using Binder, Docker, or Conda) to do this.

## Key Learning Objectives

1. Learn the basics about the data sets (pre-IceBridge, IceBridge, ICESat/GLAS and ICESat-2) served by the IceFlow library.

2. Learn to access these data sets using the IceFlow user interface widget.

3. Learn to access these data sets using the IceFlow API.

4. Learn to read and analyze the data using IceFlow.
