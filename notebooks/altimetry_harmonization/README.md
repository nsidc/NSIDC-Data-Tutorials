# Altimetry Harmonization

## Summary

These notebooks provide information about how to access and work with
airborne altimetry and related data sets from NASA’s
[IceBridge](https://www.nasa.gov/mission_pages/icebridge/index.html) mission,
and satellite altimetry data from
[ICESat/GLAS](https://icesat.gsfc.nasa.gov/icesat/) and
[ICESat-2](https://icesat-2.gsfc.nasa.gov/). Accessing and combining data from
these different missions can be difficult as file formats and coordinate
reference systems changed over time.

The [0_introduction.ipynb](./0_introduction.ipynb) notebbook provides a
descriptive background on the data.

The [corrections.ibynb](./corrections.ibynb) notebook prodvides a small example
of how to perform ITRF coordinate transformations to facilitate data comparison
across datasets.


## Setup

To run the notebooks provided in this folder, please see the
[NSIDC-Data-Tutorials repository
readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions
on several ways (using Binder, Docker, or Conda) to do this.

## Key Learning Objectives

1. Learn the basics about the data sets (pre-IceBridge, IceBridge, ICESat/GLAS and ICESat-2).
2. Learn about how ITRF coordinate transformations facilitate data comparison across datasets.
