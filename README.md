# NSIDC-Data-Tutorials

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nsidc/NSIDC-Data-Tutorial/master?urlpath=lab/tree/notebook)

## Summary

This combined repository includes tutorials and code resources provided by the NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC). These tutorials are provided as Python-based Jupyter notebooks that provide guidance on working with various data products, including how to access, subset, transform, and visualize the data provided by the NSIDC DAAC. Please see the README files associated with each individual tutorial folder for more information on each tutorial and their learning objectives. 

## Tutorials

### SnowEx_ASO_Snow_Depth

<ins>Let It Snow! Accessing and Analyzing Snow Data at the NSIDC DAAC</ins> 

Originally demonstrated through the NASA Earthdata Webinar series, this tutorial provides guidance on how to discover, access, and couple snow data across varying geospatial scales from NASA's SnowEx, Airborne Snow Observatory, and Moderate Resolution Imaging Spectroradiometer (MODIS) missions. The tutorial highlights the ability to search and access data by a defined region, and combine and compare snow data across different data formats and scales using a Python-based Jupyter Notebook.

### ICESat-2_MODIS_Arctic_Sea_Ice

<ins>Getting the most out of NSIDC DAAC data: Discovering, Accessing, and Harmonizing Arctic Remote Sensing Data</ins>

This tutorial demonstrates the NSIDC DAAC's data discovery, access, and subsetting services, along with basic open source resources used to harmonize and analyze data across multiple products. The tutorial is provided as a series of Python-based Jupyter Notebooks, focusing on sea ice height and ice surface temperature data from NASA’s ICESat-2 and MODIS missions, respectively, to characterize Arctic sea ice. 

## Usage with Binder

The Binder button above allows you to explore and run the notebook in a shared cloud computing environment without the need to install dependencies on your local machine. Note that this option will not directly download data to your computer; instead the data will be downloaded to the cloud environment.

## Usage with Conda

Install miniconda3 (Python 3.7) for your platform from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

Download the [NSIDC-Data-Tutorials](https://github.com/nsidc/NSIDC-Data-Tutorials) repository from Github by clicking the green 'Clone or Download' button located at the top right of the repository page.

Unzip the file, and open a command line or terminal window in the NSIDC-Data-Tutorials folder's location.

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

This should open a browser window with the JupyterLab IDE, showing your current working directory on the left-hand navigation. Navigate to the tutorial folder of choice and click on their associated *.ipynb files to get started.  


 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
