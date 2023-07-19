# ICESat-2 Cloud Access 

## Summary
This notebook demonstrates searching for cloud-hosted ICESat-2 data and directly accessing Land Ice Height (ATL06) granules from an Amazon Compute Cloud (EC2) instance using the `earthaccess` package. NASA data "in the cloud" are stored in Amazon Web Services (AWS) Simple Storage Service (S3) Buckets. **Direct Access** is an efficient way to work with data stored in an S3 Bucket when you are working in the cloud. Cloud-hosted granules can be opened and loaded into memory without the need to download them first. This allows you take advantage of the scalability and power of cloud computing.

## Set up
To run the notebook provided in this folder in the Amazon Web Services (AWS) cloud, there are a couple of options:
* An EC2 instance already set up with the necessary software installed to run a Jupyter notebook, and the environment set up using the provided environment.yml file. **Note:** If you are running this notebook on your own AWS EC2 instance using the environment set up using the environment.yml file in the NSIDC-Data-Tutorials/notebooks/ICESat-2_Cloud_Access/environment folder, you may need to run the following command before running the notebook to ensure the notebook executes properly:

`jupyter nbextension enable --py widgetsnbextension`

    You do NOT need to do this if you are using the environment set up using the environment.yml file from the NSIDC-Data-Tutorials/binder folder.
    
* Alternatively, if you have access to one, it can be run in a managed cloud-based Jupyter hub. Just make sure all the necessary libraries are installed (`earthaccess`,`xarray`, and `hvplot`). 

For further details on the prerequisites, see the 'Prerequisites' section in the notebook. 

## Key Learning Objectives 

1. Use `earthaccess` to search for ICESat-2 data using spatial and temporal filters and explore search results;
2. Open data granules using direct access to the ICESat-2 S3 bucket;
3. Load a HDF5 group into an `xarray.Dataset`;
4. Visualize the land ice heights using `hvplot`.

