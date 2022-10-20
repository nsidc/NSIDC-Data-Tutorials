# to get and use geojson datacube catalog
import json
import logging
# for timing data access
import time

import numpy as np
import pyproj
import s3fs as s3
# for datacube xarray/zarr access
import xarray as xr
# for plotting time series
from shapely import geometry

logging.basicConfig(level=logging.ERROR)
# import pandas as pd


# class to throw time series lookup errors
class timeseriesException(Exception):
    pass


class DATACUBETOOLS:
    """
    class to encapsulate discovery and interaction with ITS_LIVE (its-live.jpl.nasa.gov) datacubes on AWS s3
    """

    VELOCITY_DATA_ATTRIBUTION = """ \nITS_LIVE velocity data
    (<a href="https://its-live.jpl.nasa.gov">ITS_LIVE</a>) with funding provided by NASA MEaSUREs.\n
    """

    def __init__(self, use_catalog="all"):
        """
        tools for accessing ITS_LIVE glacier velocity datacubes in S3
        __init__ reads in the geojson catalog of datacubes and creates list .open_cubes
        """
        # the URL for the current datacube catalog GeoJSON file - set up as dictionary to allow other catalogs for testing
        self.catalog = {
            "all": "s3://its-live-data/datacubes/catalog_v02.json",
        }

        # S3fs used to access cubes in python
        self._s3fs = s3.S3FileSystem(anon=True)
        # keep track of open cubes so that we don't re-read xarray metadata and dimension vectors
        self.open_cubes = {}
        self._current_catalog = use_catalog
        with self._s3fs.open(self.catalog[use_catalog], "r") as incubejson:
            self._json_all = json.load(incubejson)
        self.json_catalog = self._json_all

    def find_datacube_catalog_entry_for_point(self, point_xy, point_epsg_str):
        """
        find catalog feature that contains the point_xy [x,y] in projection point_epsg_str (e.g. '3413')
        returns the catalog feature and the point_tilexy original point coordinates reprojected into the datacube's native projection
        (cubefeature, point_tilexy)
        """
        if point_epsg_str != "4326":
            # point not in lon,lat, set up transformation and convert it to lon,lat (epsg:4326)
            # because the features in the catalog GeoJSON are polygons in 4326
            inPROJtoLL = pyproj.Transformer.from_proj(
                f"epsg:{point_epsg_str}", "epsg:4326", always_xy=True
            )
            pointll = inPROJtoLL.transform(*point_xy)
        else:
            # point already lon,lat
            pointll = point_xy

        # create Shapely point object for inclusion test
        point = geometry.Point(*pointll)  # point.coords.xy

        # find datacube outline that contains this point in geojson index file
        cubefeature = None

        for f in self.json_catalog["features"]:
            polygeom = geometry.shape(f["geometry"])
            if polygeom.contains(point):
                cubefeature = f
                break

        if cubefeature:
            # find point x and y in cube native epsg if not already in that projection
            if point_epsg_str == str(cubefeature["properties"]["epsg"]):
                point_cubexy = point_xy
            else:
                inPROJtoTilePROJ = pyproj.Transformer.from_proj(
                    f"epsg:{point_epsg_str}",
                    f"EPSG:{cubefeature['properties']['epsg']}",
                    always_xy=True,
                )
                point_cubexy = inPROJtoTilePROJ.transform(*point_xy)

            print(
                f"original xy {point_xy} {point_epsg_str} maps to datacube {point_cubexy} "
                f"EPSG:{cubefeature['properties']['epsg']}"
            )

            # now test if point is in xy box for cube (should be most of the time; could fail
            # because of boundary curvature 4326 box defined by lon,lat corners but point needs to be in box defined in cube's projection)
            #
            point_cubexy_shapely = geometry.Point(*point_cubexy)
            polygeomxy = geometry.shape(cubefeature["properties"]["geometry_epsg"])
            if not polygeomxy.contains(point_cubexy_shapely):
                # first find cube proj bounding box
                dcbbox = np.array(
                    cubefeature["properties"]["geometry_epsg"]["coordinates"][0]
                )
                minx = np.min(dcbbox[:, 0])
                maxx = np.max(dcbbox[:, 0])
                miny = np.min(dcbbox[:, 1])
                maxy = np.max(dcbbox[:, 1])

                # point is in lat lon box, but not in cube-projection's box
                # try once more to find proper cube by using a new point in cube projection moved 10 km farther from closest
                # boundary in cube projection; use new point's lat lon to search for new cube - test if old point is in that
                # new cube's projection box, otherwise ...
                # this next section tries one more time to find new feature after offsetting point farther outside box of
                # first cube, in cube projection, to deal with curvature of lat lon box edges in different projections
                #
                # point in ll box but not cube_projection box, move point in cube projection
                # 10 km farther outside box, find new ll value for point, find new feature it is in,
                # and check again if original point falls in this new cube's
                # move coordinate of point outside this box farther out by 10 km

                newpoint_cubexy = list(point_cubexy)
                if point_cubexy[1] < miny:
                    newpoint_cubexy[1] -= 10000.0
                elif point_cubexy[1] > maxy:
                    newpoint_cubexy[1] += 10000.0
                elif point_cubexy[0] < minx:
                    newpoint_cubexy[0] -= 10000.0
                elif point_cubexy[0] > maxx:
                    newpoint_cubexy[0] += 10000.0
                else:
                    # no change has been made to newpoint_cubexy because
                    # user has chosen a point exactly on the boundary, move it 1 m into the box...
                    logging.info(
                        "user has chosen a point exactly on the boundary, move it 1 m into the box..."
                    )
                    if point_cubexy[1] == miny:
                        newpoint_cubexy[1] += 1.0
                    elif point_cubexy[1] == maxy:
                        newpoint_cubexy[1] -= 1.0
                    elif point_cubexy[0] == minx:
                        newpoint_cubexy[0] += 1.0
                    elif point_cubexy[0] == maxx:
                        newpoint_cubexy[0] -= 1.0

                # now reproject this point to lat lon and look for new feature

                cubePROJtoLL = pyproj.Transformer.from_proj(
                    f'{cubefeature["properties"]["data_epsg"]}',
                    "epsg:4326",
                    always_xy=True,
                )
                newpointll = cubePROJtoLL.transform(*newpoint_cubexy)

                # create Shapely point object for inclusion test
                newpoint = geometry.Point(*newpointll)

                # find datacube outline that contains this point in geojson index file
                newcubefeature = None

                for f in self.json_catalog["features"]:
                    polygeom = geometry.shape(f["geometry"])
                    if polygeom.contains(newpoint):
                        newcubefeature = f
                        break

                if newcubefeature:
                    # if new feature found, see if original (not offset) point is in this new cube's cube-projection bounding box
                    # find point x and y in cube native epsg if not already in that projection
                    if (
                        cubefeature["properties"]["data_epsg"]
                        == newcubefeature["properties"]["data_epsg"]
                    ):
                        point_cubexy = newpoint_cubexy
                    else:
                        # project original point in this new cube's projection
                        inPROJtoTilePROJ = pyproj.Transformer.from_proj(
                            f"epsg:{point_epsg_str}",
                            newcubefeature["properties"]["data_epsg"],
                            always_xy=True,
                        )
                        point_cubexy = inPROJtoTilePROJ.transform(*point_xy)

                    logging.info(
                        f"try 2 original xy {point_xy} {point_epsg_str} with offset maps to new datacube {point_cubexy} "
                        f" {newcubefeature['properties']['data_epsg']}"
                    )

                    # now test if point is in xy box for cube (should be most of the time;
                    #
                    point_cubexy_shapely = geometry.Point(*point_cubexy)
                    polygeomxy = geometry.shape(
                        newcubefeature["properties"]["geometry_epsg"]
                    )
                    if not polygeomxy.contains(point_cubexy_shapely):
                        # point is in lat lon box, but not in cube-projection's box
                        # try once more to find proper cube by using a new point in cube projection moved 10 km farther from closest
                        # boundary in cube projection; use new point's lat lon to search for new cube - test if old point is in that
                        # new cube's projection box, otherwise fail...

                        raise timeseriesException(
                            f"point is in lat,lon box but not {cubefeature['properties']['data_epsg']} box!! even after offset"
                        )
                    else:
                        return (newcubefeature, point_cubexy)

            else:
                return (cubefeature, point_cubexy)

        else:
            print(f"No data for point (lon,lat) {pointll}")
            return (None, None)

    def get_timeseries_at_point(self, point_xy, point_epsg_str, variables=["v"]):
        """pulls time series for a point (closest ITS_LIVE point to given location):
        - calls find_datacube to determine which S3-based datacube the point is in,
        - opens that xarray datacube - which is also added to the open_cubes list, so that it won't need to be reopened (which can take O(5 sec) ),
        - extracts time series at closest grid cell to the original point
            (time_series.x and time_series.y contain x and y coordinates of ITS_LIVE grid cell in datacube projection)

        returns(
            - xarray of open full cube (not loaded locally, but coordinate vectors and attributes for full cube are),
            - time_series (as xarray dataset with all requested variables, that is loaded locally),
            - original point xy in datacube's projection
            )

        NOTE - returns an xarray Dataset (not just a single xarray DataArray) - time_series.v or time_series['v'] is speed
        """

        start = time.time()

        cube_feature, point_cubexy = self.find_datacube_catalog_entry_for_point(
            point_xy, point_epsg_str
        )

        if cube_feature is None:
            return (None, None, None)

        # for zarr store modify URL for use in boto open - change http: to s3: and lose s3.amazonaws.com
        incubeurl = (
            cube_feature["properties"]["zarr_url"]
            .replace("http:", "s3:")
            .replace(".s3.amazonaws.com", "")
        )

        # if we have already opened this cube, don't open it again
        if len(self.open_cubes) > 0 and incubeurl in self.open_cubes.keys():
            ins3xr = self.open_cubes[incubeurl]
        else:
            ins3xr = xr.open_dataset(
                incubeurl, engine="zarr", storage_options={"anon": True}
            )
            self.open_cubes[incubeurl] = ins3xr

        # find time series at the closest grid cell
        # NOTE - returns an xarray Dataset - pt_dataset.v is speed...
        pt_datset = ins3xr[variables].sel(
            x=point_cubexy[0], y=point_cubexy[1], method="nearest"
        )

        logging.info(
            f"xarray open - elapsed time: {(time.time()-start):10.2f}", flush=True
        )

        # pull data to local machine
        pt_datset.load()

        # print(
        #     f"time series loaded {[f'{x}: {pt_datset[x].shape[0]}' for x in variables]} points - elapsed time: {(time.time()-start):10.2f}",
        #     flush=True,
        # )
        # end for zarr store

        return (ins3xr, pt_datset, point_cubexy)

    def set_mapping_for_small_cube_from_larger_one(self, smallcube, largecube):
        """when a subset is pulled from an ITS_LIVE datacube, a new geotransform needs to be
        figured out from the smallcube's x and y coordinates and stored in the GeoTransform attribute
        of the mapping variable (which also needs to be copied from the original cube)
        """
        largecube_gt = [float(x) for x in largecube.mapping.GeoTransform.split(" ")]
        smallcube_gt = largecube_gt  # need to change corners still
        # find UL corner of UL pixel (x and y are pixel center coordinates)
        smallcube_gt[0] = smallcube.x.min().item() - (
            smallcube_gt[1] / 2.0
        )  # set new ul x value
        smallcube_gt[3] = smallcube.y.max().item() - (
            smallcube_gt[5] / 2.0
        )  # set new ul y value
        smallcube[
            "mapping"
        ] = largecube.mapping  # still need to add new GeoTransform as string
        smallcube.mapping["GeoTransform"] = " ".join([str(x) for x in smallcube_gt])
        return

    def get_subcube_around_point(
        self, point_xy, point_epsg_str, half_distance=5000.0, variables=["v"]
    ):
        """pulls subset of cube within half_distance of point (unless edge of cube is included) containing specified variables:
        - calls find_datacube to determine which S3-based datacube the point is in,
        - opens that xarray datacube - which is also added to the open_cubes list, so that it won't need to be reopened (which can take O(5 sec) ),
        - extracts smaller cube containing full time series of specified variables

        returns(
            - xarray of open full cube (not loaded locally, but coordinate vectors and attributes for full cube are),
            - smaller cube as xarray,
            - original point xy in datacube's projection
            )
        """

        start = time.time()

        cube_feature, point_cubexy = self.find_datacube_catalog_entry_for_point(
            point_xy, point_epsg_str
        )

        # for zarr store modify URL for use in boto open - change http: to s3: and lose s3.amazonaws.com
        incubeurl = (
            cube_feature["properties"]["zarr_url"]
            .replace("http:", "s3:")
            .replace(".s3.amazonaws.com", "")
        )

        # if we have already opened this cube, don't open it again
        if len(self.open_cubes) > 0 and incubeurl in self.open_cubes.keys():
            ins3xr = self.open_cubes[incubeurl]
        else:
            ins3xr = xr.open_dataset(
                incubeurl, engine="zarr", storage_options={"anon": True}
            )
            self.open_cubes[incubeurl] = ins3xr

        pt_tx, pt_ty = point_cubexy
        lx = ins3xr.coords["x"]
        ly = ins3xr.coords["y"]

        start = time.time()
        small_ins3xr = (
            ins3xr[variables]
            .loc[
                dict(
                    x=lx[(lx > pt_tx - half_distance) & (lx < pt_tx + half_distance)],
                    y=ly[(ly > pt_ty - half_distance) & (ly < pt_ty + half_distance)],
                )
            ]
            .load()
        )
        print(f"subset and load at {time.time() - start:6.2f} seconds", flush=True)

        # now fix the CF compliant geolocation/mapping of the smaller cube
        self.set_mapping_for_small_cube_from_larger_one(small_ins3xr, ins3xr)

        return (ins3xr, small_ins3xr, point_cubexy)

    def get_subcube_for_bounding_box(self, bbox, bbox_epsg_str, variables=["v"]):
        """pulls subset of cube within bbox (unless edge of cube is included) containing specified variables:
        - calls find_datacube to determine which S3-based datacube the bbox central point is in,
        - opens that xarray datacube - which is also added to the open_cubes list, so that it won't need to be reopened (which can take O(5 sec) ),
        - extracts smaller cube containing full time series of specified variables

        bbox = [ minx, miny, maxx, maxy ] in bbox_epsg_str meters
        bbox_epsg_str = '3413', '32607', '3031', ... (EPSG:xxxx) projection identifier
        variables = [ 'v', 'vx', 'vy', ...] variables in datacube - note 'mapping' is returned by default, with updated geotransform attribute for the new subcube size

        returns(
            - xarray of open full cube (not loaded locally, but coordinate vectors and attributes for full cube are),
            - smaller cube as xarray (loaded to memory),
            - original bbox central point xy in datacube's projection
            )
        """

        start = time.time()

        #
        # derived from point/distance (get_subcube_around_point) so first iteration uses central point to look up datacube to open
        # subcube will still be clipped at datacube edge if bbox extends to other datacubes - in future maybe return subcubes from each?
        #
        # bbox is probably best expressed in datacube epsg - will fail if different...  in future, deal with this some other way.
        #

        bbox_minx, bbox_miny, bbox_maxx, bbox_maxy = bbox
        bbox_centrer_point_xy = [
            (bbox_minx + bbox_maxx) / 2.0,
            (bbox_miny + bbox_maxy) / 2.0,
        ]
        (
            cube_feature,
            bbox_centrer_point_cubexy,
        ) = self.find_datacube_catalog_entry_for_point(
            bbox_centrer_point_xy, bbox_epsg_str
        )

        if cube_feature["properties"]["data_epsg"].split(":")[-1] != bbox_epsg_str:
            print(
                f'bbox is in epsg:{bbox_epsg_str}, should be in datacube {cube_feature["properties"]["data_epsg"]}'
            )
            return None

        # for zarr store modify URL for use in boto open - change http: to s3: and lose s3.amazonaws.com
        incubeurl = (
            cube_feature["properties"]["zarr_url"]
            .replace("http:", "s3:")
            .replace(".s3.amazonaws.com", "")
        )

        # if we have already opened this cube, don't open it again
        if len(self.open_cubes) > 0 and incubeurl in self.open_cubes.keys():
            ins3xr = self.open_cubes[incubeurl]
        else:
            # open zarr format xarray datacube on AWS S3
            ins3xr = xr.open_dataset(
                incubeurl, engine="zarr", storage_options={"anon": True}
            )
            self.open_cubes[incubeurl] = ins3xr

        lx = ins3xr.coords["x"]
        ly = ins3xr.coords["y"]

        start = time.time()
        small_ins3xr = (
            ins3xr[variables]
            .loc[
                dict(
                    x=lx[(lx >= bbox_minx) & (lx <= bbox_maxx)],
                    y=ly[(ly >= bbox_miny) & (ly <= bbox_maxy)],
                )
            ]
            .load()
        )
        print(f"subset and load at {time.time() - start:6.2f} seconds", flush=True)

        # now fix the CF compliant geolocation/mapping of the smaller cube
        self.set_mapping_for_small_cube_from_larger_one(small_ins3xr, ins3xr)

        return (ins3xr, small_ins3xr, bbox_centrer_point_cubexy)
