# ICESat-2 Cloud Access 

## Summary
This notebook demonstrates searching for cloud-hosted ICESat-2 data and directly accessing Land Ice Height (ATL06) granules from an Amazon Compute Cloud (EC2) instance using the `earthaccess` package. NASA data "in the cloud" are stored in Amazon Web Services (AWS) Simple Storage Service (S3) Buckets. **Direct Access** is an efficient way to work with data stored in an S3 Bucket when you are working in the cloud. Cloud-hosted granules can be opened and loaded into memory without the need to download them first. This allows you take advantage of the scalability and power of cloud computing.

## Set up
To run the notebook provided in this folder, please see the [NSIDC-Data-Tutorials repository readme](https://github.com/nsidc/NSIDC-Data-Tutorials#readme) for instructions on several ways (using Binder, Docker, or Conda) to do this.

## Key Learning Objectives 

1. Use `earthaccess` to search for ICESat-2 data using spatial and temporal filters and explore search results;
2. Open data granules using direct access to the ICESat-2 S3 bucket;
3. Load a HDF5 group into an `xarray.Dataset`;
4. Visualize the land ice heights using `hvplot`.

