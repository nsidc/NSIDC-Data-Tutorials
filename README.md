# NSIDC-Data-Tutorial

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nsidc/NSIDC-Data-Tutorial/master?urlpath=lab/tree/notebook)
## Presenters

Amy Steiker, Walt Meier: NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC)

## Authors

Amy Steiker, Bruce Wallin, Andy Barrett, Walt Meier, Luis Lopez, Marin Klinger: NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC)

## Summary

The NSIDC DAAC provides a wide variety of remote sensing data on the cryosphere, often with disparate coverage and resolution. This tutorial will demonstrate our data discovery, access, and subsetting services, along with basic open source resources used to harmonize and analyze data across these diverse products. The tutorial will be presented as a series of Python-based Jupyter Notebooks, focusing on sea ice height and ice surface temperature data from NASA’s ICESat-2 and MODIS missions, respectively, to characterize Arctic sea ice. No coding experience or computing prerequisites are required, though some familiarity with Python and Jupyter Notebooks is recommended. The in-person tutorial utilized a JupyterHub environment that was preconfigured with the dependencies needed to run each operation in the series of notebooks. For those of you interested in running the notebooks outside of the in-person event, see below for details on how to run using Binder and Conda. 

## Key Learning Objectives

1) Become familiar with NSIDC resources, including user support documents, data access options, and data subsetting services.

2) Learn how to access and subset data programmatically using the NSIDC DAAC's API service. 

3) Learn about the coverage, resolution, and structure of sea ice data from new NASA ICESat-2 mission.

3) Interact with ICESat-2 and MODIS data using basic Python science libraries to visualize, filter, and plot concurrent data.


## Usage with Binder

The Binder button above allows you to explore and run the notebook in a shared cloud computing environment without the need to install dependencies on your local machine. Note that this option will not directly download data to your computer; instead the data will be downloaded to the cloud environment.

## Usage with Conda

Install miniconda3 (Python 3.7) for your platform from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

Download the [NSIDC-Data-Tutorial](https://github.com/nsidc/NSIDC-Data-Tutorial) repository from Github by clicking the green 'Clone or Download' button located at the top right of the repository page.

Unzip the file, and open a command line or terminal window in the AGU-2019-NSIDC-Data-Tutorial folder's location.

From a command line or terminal window, install the required environment with the following command:

```bash
conda env create -f binder/environment.yml
```

you should now see that the dependencies were installed and our environment is ready to be used.

Activate the environment with

```
conda activate tutorial
```

Launch the notebook locally with the following command:

```bash
jupyter lab
```

This should open a browser window with the JupyterLab IDE, showing your current working directory on the left-hand navigation. Navigate to the notebooks folder and click on Introduction.ipynb file to get started.


 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
