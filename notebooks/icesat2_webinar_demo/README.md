# Laser Altimetry Applications for a Changing World: Working with ICESat-2 Sea Ice Data

## Overview
This directory contains a notebook demonstrating how to work with ICESat-2 Sea Ice Data using `earthaccess`, `xarray` and `matplotlib`.

The demo was presented at the NASA Earthdata Webinar held on Wednesday, 6 August, 2025.

## Learning Outcomes

1. How to search for ICESat-2 data sets (collections) using `earthaccess`.
2. How to search for data files using a time range and spatial extent.
3. How to open an ATL07 and ATL10 using `xarray`
4. How to make a simple plot of ATL07 data using `matplotlib`

## Setup

You will need at least version 2024.10.1 of `xarray` and version 0.14.0 of `earthaccess` for this tutorial.  We recommend creating a virtual environment using the `environment.yml` file in the environment folder using `mamba` or `conda`.

```
mamba env update -f environment/environment.yml
```
or
```
conda env update -f environment/environment.yml
```

This will create an virtual environment called `nsidc-tutorial-icesat2-apps`.

To activate the environment.

```
mamba activate nsidc-tutorial-icesat2-apps
```
or
```
conda activate nsidc-tutorial-icesat2-apps
```

You can now launch Jupyter Lab and navigate to `working_with_icesat2_sea_ice_data.ipynb`.

## Bugs

<Add-link-to-github-issues>