# ICESat-2 Cloud Access 

## Summary
We provide several notebooks showcasing how to search and access ICESat-2 from the NASA Earthdata Cloud. NASA data "in the cloud" are stored in Amazon Web Services (AWS) Simple Storage Service (S3) Buckets. **Direct Access** is an efficient way to work with data stored in an S3 Bucket when you are working in the cloud. Cloud-hosted granules can be opened and loaded into memory without the need to download them first. This allows you take advantage of the scalability and power of cloud computing.

### [Accessing and working with ICESat-2 data in the cloud](./ATL06-direct-access_rendered.ipynb)
This notebook demonstrates searching for cloud-hosted ICESat-2 data and directly accessing Land Ice Height (ATL06) granules from an Amazon Compute Cloud (EC2) instance using the `earthaccess` package. 

#### Key Learning Objectives 
1. Use `earthaccess` to search for ICESat-2 data using spatial and temporal filters and explore search results;
2. Open data granules using direct access to the ICESat-2 S3 bucket;
3. Load a HDF5 group into an `xarray.Dataset`;
4. Visualize the land ice heights using `hvplot`.

### [Plotting ICESat-2 and CryoSat-2 Freeboards](./ICESat2-CryoSat2-Coincident.ipynb)
This notebook demonstrates plotting coincident ICESat-2 and CryoSat-2 data in the same map from within an AWS ec2 instance.  ICESat-2 data are accessed via "direct S3 access" using `earthaccess`.  CryoSat-2 data are downloaded to our cloud instance from their ftp storage lcoation and accessed locally.  

#### Key Learning Objectives 
1. use `earthaccess` to search for ICESat-2 ATL10 data using a spatial filter
2. open cloud-hosted files using direct access to the ICESat-2 S3 bucket; 
3. use cs2eo script to download files into your hub instance
3. load an HDF5 group into an `xarray.Dataset`;  
4. visualize freeboards using `hvplot`.
5. map the locations of ICESat-2 and CryoSat-2 freeboards using `cartopy`

### [Processing Large-scale Time Series of ICESat-2 Sea Ice Height in the Cloud](./ATL10-h5coro_rendered.ipynb)
This notebook utilizes several libraries to performantly search, access, read, and grid ATL10 data over the Ross Sea, Antarctica including `earthaccess`, `h5coro`, and `geopandas`. The notebook provides further guidance on how to scale this analysis to the entire continent, running the same workflow from a script that can be run from your laptop using [Coiled](https://www.coiled.io/).

#### Key Learning Objectives 
1. Use earthaccess to authenticate with Earthdata Login, search for ICESat-2 data using spatial and temporal filters, and directly access files in the cloud.
2. Open data granules using h5coro to efficiently read HDF5 data from the NSIDC DAAC S3 bucket.
3. Load data into a geopandas.DataFrame containing geodetic coordinates, ancillary variables, and date/time converted from ATLAS Epoch.
4. Grid track data to EASE-Grid v2 6.25 km projected grid using drop-in-the-bucket resampling.
5. Calculate mean statistics and assign aggregated data to grid cells.
6. Visualize aggregated sea ice height data on a map.

## Set up
To run the notebooks provided in this folder in the Amazon Web Services (AWS) cloud, there are a couple of options:
* An EC2 instance already set up with the necessary software installed to run a Jupyter notebook, and the environment set up using the provided environment.yml file. **Note:** If you are running these notebooks on your own AWS EC2 instance using the environment set up using the environment.yml file in the NSIDC-Data-Tutorials/notebooks/ICESat-2_Cloud_Access/environment folder, you may need to run the following command before running the notebook to ensure the notebook executes properly:

`jupyter nbextension enable --py widgetsnbextension`

    You do NOT need to do this if you are using the environment set up using the environment.yml file from the NSIDC-Data-Tutorials/binder folder.
    
* Alternatively, if you have access to one, it can be run in a managed cloud-based Jupyter hub. Just make sure all the necessary libraries are installed (e.g. `earthaccess`,`xarray`,`hvplot`, etc.). 

For further details on the prerequisites, see the 'Prerequisites' section in each notebook. 



