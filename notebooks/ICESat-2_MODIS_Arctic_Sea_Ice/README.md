> [!WARNING]  
> Data access is no longer possible using the method described in this tutorial

This tutorial was developed for a workshop presented at AGU 2019 and represents a snapshot in time.  The data access method described below was developed to access data within NSIDC DAAC’s legacy, on-premises archive.  Data have since migrated to the NASA Earthdata Cloud and are not accessible as described below.  NASA Earthdata Cloud data are freely accessible for download or in-region (AWS us-west-2) access to anyone with an Earthdata Login.  We are developing material to replace the instructions presented here.  In the meantime, we recommend the following tutorials for programmatic data access:

https://github.com/nsidc/NSIDC-Data-Tutorials/tree/main/notebooks/ICESat-2_Cloud_Access

https://nasa-openscapes.github.io/earthdata-cloud-cookbook/tutorials/IS2_Harmony

For more information regarding the migration and data access from NASA Earthdata Cloud please go here:

https://nsidc.org/data/user-resources/help-center/nasa-earthdata-cloud-data-access-guide

# AGU-2019-NSIDC-Data-Tutorial


## Presenters

Amy Steiker, Walt Meier: NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC)

## Authors

Amy Steiker, Bruce Wallin, Andy Barrett, Walt Meier, Luis Lopez, Marin Klinger: NASA National Snow and Ice Data Center Distributed Active Archive Center (NSIDC DAAC)

## Summary

The NSIDC DAAC provides a wide variety of remote sensing data on the cryosphere, often with disparate coverage and resolution. This tutorial will demonstrate our data discovery, access, and subsetting services, along with basic open source resources used to harmonize and analyze data across these diverse products. The tutorial will be presented as a series of Python-based Jupyter Notebooks, focusing on sea ice height and ice surface temperature data from NASA’s ICESat-2 and MODIS missions, respectively, to characterize Arctic sea ice. No coding experience or computing prerequisites are required, though some familiarity with Python and Jupyter Notebooks is recommended. The in-person tutorial utilized a JupyterHub environment that was preconfigured with the dependencies needed to run each operation in the series of notebooks. For those of you interested in running the notebooks outside of the in-person event, see the README in this NSIDC-Data-Tutorial repository for details on how to run using Binder and Conda. 


## Key Learning Objectives

1) Become familiar with NSIDC resources, including user support documents, data access options, and data subsetting services.

2) Learn how to access and subset data programmatically using the NSIDC DAAC's API service. 

3) Learn about the coverage, resolution, and structure of sea ice data from new NASA ICESat-2 mission.

3) Interact with ICESat-2 and MODIS data using basic Python science libraries to visualize, filter, and plot concurrent data.
