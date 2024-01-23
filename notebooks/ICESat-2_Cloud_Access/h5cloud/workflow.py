#!/usr/bin/env python

import coiled

import geopandas as gpd
import numpy as np
import pandas as pd
from rich import print as rprint
from itertools import product
import argparse

import earthaccess
from h5coro import h5coro, s3driver

from read_atl10 import read_atl10

if __name__ == "__main__":

    rprint(f"executing locally")
    parser = argparse.ArgumentParser()
    parser.add_argument('--bbox', help='bbox')
    parser.add_argument('--year', help='year to process')
    parser.add_argument('--env', help='execute in the cloud or local, default:local')
    parser.add_argument('--out', help='output file name')
    args = parser.parse_args()


    auth = earthaccess.login()

    # ross_sea = (-180, -78, -160, -74)
    # antarctic = (-180, -90, 180, -60)

    year = int(args.year)
    bbox = tuple([float(c) for c in args.bbox.split(",")])

    print(f"Searching ATL10 data for year {year} ...")
    granules = earthaccess.search_data(
        short_name = 'ATL10',
        version = '006',
        cloud_hosted = True,
        bounding_box = bbox,
        temporal = (f'{args.year}-06-01',f'{args.year}-09-30'),
        count=4,
        debug=True
    )


    if args.env == "local":
        files = [g.data_links(access="out_of_region")[0] for g in granules]
        credentials = earthaccess.__auth__.token["access_token"]

        df = read_atl10(files, bounding_box=args.bbox, environment="local", credentials=credentials)
    else:
        files = [g.data_links(access="direct")[0].replace("s3://", "") for g in granules]
        aws_credentials = earthaccess.get_s3_credentials("NSIDC")
        credentials = {
          "aws_access_key_id": aws_credentials["accessKeyId"],
          "aws_secret_access_key": aws_credentials["secretAccessKey"],
          "aws_session_token": aws_credentials["sessionToken"]
        }

        @coiled.function(region= "us-west-2",
                         memory= "4 GB",
                         keepalive="1 HOUR")
        def cloud_runnner(files, bounding_box, credentials):
            df = read_atl10(files, bounding_box=bounding_box, environment="cloud", credentials=credentials)
            return df

        df = cloud_runnner(files, args.bbox, credentials=credentials)


    df.to_parquet(f"{args.out}.parquet")
    rprint(df)

