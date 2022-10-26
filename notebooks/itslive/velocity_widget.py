# for timing data access
import shutil
import time
import zipfile
from pathlib import Path
from uuid import uuid4

import ipyleaflet
import ipywidgets
import numpy as np
import pandas as pd
# to get and use geojson datacube catalog
# for datacube xarray/zarr access
from IPython.display import display
# for plotting time series
from matplotlib import pyplot as plt

# import itslive datacube tools for working with cloun-based datacubes
from datacube_tools import DATACUBETOOLS as dctools


class ITSLIVE:
    """
    Class to encapsulate ITS_LIVE plotting from zarr in S3
    """

    VELOCITY_ATTRIBUTION = """ \nITS_LIVE velocity mosaic
    (<a href="https://its-live.jpl.nasa.gov">ITS_LIVE</a>) with funding provided by NASA MEaSUREs.\n
    """

    def __init__(self, *args, **kwargs):
        """
        Map widget to plot glacier velocities
        """
        self.dct = (
            dctools()
        )  # initializes geojson catalog and open cubes list for this object
        self.config = {
            "plot": "v",
            "min_separation_days": 5,
            "max_separation_days": 90,
            "color_by": "location",
            "verbose": False,
            "running_mean": True,
            "coords": None,
            "data_link": None,
        }

        self.directory_session = uuid4()

        self.ts = []

        self.color_index = 0
        self.icon_color_index = 0
        self._last_click = None
        self.fig, self.ax = plt.subplots(1, 1)

        self._initialize_widgets()

    def set_config(self, config):
        self.config = config

    def _initialize_widgets(self, projection="global"):
        self._control_plot_running_mean_checkbox = ipywidgets.Checkbox(
            value=True,
            description="Include running mean",
            disabled=False,
            indent=False,
            tooltip="Plot running mean through each time series",
            layout=ipywidgets.Layout(width="150px"),
        )
        self._control_plot_running_mean_widgcntrl = ipyleaflet.WidgetControl(
            widget=self._control_plot_running_mean_checkbox, position="bottomright"
        )
        self._control_clear_points_button = ipywidgets.Button(
            description="Clear Points", tooltip="clear all picked points"
        )
        self._control_clear_points_button.on_click(self.clear_points)

        self._control_clear_points_button_widgcntrl = ipyleaflet.WidgetControl(
            widget=self._control_clear_points_button, position="bottomright"
        )

        self._control_plot_button = ipywidgets.Button(
            description="Draw Marker", tooltip="click to make plot"
        )
        self._control_plot_button.style.button_color = "lightgreen"
        self._control_plot_button.on_click(self.plot_time_series)
        self._control_plot_button_widgcntrl = ipyleaflet.WidgetControl(
            widget=self._control_plot_button, position="bottomleft"
        )

        self._map_base_layer = ipyleaflet.basemap_to_tiles(
            {
                "url": (
                    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/"
                    "MapServer/tile/{z}/{y}/{x}.jpg"
                ),
                "attribution": "\nImagery provided by ESRI\n",
                "name": "ESRI basemap",
            }
        )
        self._map_velocity_layer = ipyleaflet.basemap_to_tiles(
            {
                "url": "https://glacierflow.nyc3.digitaloceanspaces.com/webmaps/vel_map/{z}/{x}/{y}.png",
                "attribution": self.VELOCITY_ATTRIBUTION,
                "name": "ITS_LIVE Velocity Mosaic",
            }
        )
        self._map_coverage_layer = ipyleaflet.GeoJSON(
            data=self.dct.json_catalog,
            name="ITS_LIVE datacube coverage",
            style={
                "opacity": 0.8,
                "fillOpacity": 0.2,
                "weight": 1,
                "color": "red",
                "cursor": "crosshair",
            },
            hover_style={
                "color": "white",
                "dashArray": "0",
                "fillOpacity": 0.5,
            },
        )
        self.map = ipyleaflet.Map(
            basemap=self._map_base_layer,
            double_click_zoom=False,
            scroll_wheel_zoom=True,
            center=[57.20, -49.43],
            zoom=4
            # layout=ipywidgets.Layout(height="100%", max_height="100%", display="flex")
        )
        self._map_picked_points_layer_group = ipyleaflet.LayerGroup(
            layers=[], name="Selected Points"
        )

        # Populating the map

        self.map.add_layer(self._map_picked_points_layer_group)
        self.map.add_layer(self._map_velocity_layer)
        # wms = ipyleaflet.WMSLayer(url="https://integration.glims.org/geoserver/GLIMS/gwc/service",
        #                           name="GLIMS glacier outlines",
        #                           layers="GLIMS:GLIMS_GLACIERS",
        #                           transparent=True,
        #                           opacity=0.33,
        #                           format='image/png')
        # self.map.add_layer(wms)
        self.map.add_control(
            ipyleaflet.MeasureControl(
                position="topleft",
                active_color="orange",
                primary_length_unit="kilometers",
            )
        )
        marker = ipyleaflet.Marker(
            icon=ipyleaflet.AwesomeIcon(
                name="check", marker_color="green", icon_color="darkgreen"
            )
        )
        self.map.add_control(ipyleaflet.FullScreenControl())
        self.map.add_control(ipyleaflet.LayersControl())
        self.map.add_control(
            ipyleaflet.SearchControl(
                position="topleft",
                url="https://nominatim.openstreetmap.org/search?format=json&q={s}",
                zoom=5,
                marker=marker,
            )
        )
        self.map.add_control(ipyleaflet.ScaleControl(position="bottomleft"))
        # self.map.add_control(self._control_plot_running_mean_widgcntrl)
        # self.map.add_control(self._control_clear_points_button_widgcntrl)
        # self.map.add_control(self._control_plot_button_widgcntrl)
        self.map.default_style = {"cursor": "crosshair"}
        self.map.on_interaction(self._handle_map_click)

    def display(self, render_sidecar=True):
        if render_sidecar:
            from sidecar import Sidecar

            if not hasattr(self, "sidecar"):
                self.sidecar = Sidecar(title="Map Widget")
            self.sidecar.clear_output()
            with self.sidecar:
                display(self.map)
        else:
            display(self.map)

    # running mean
    def runningMean(
        self,
        mid_dates,
        variable,
        minpts,
        tFreq,
    ):
        """
        mid_dates: center dates of `variable` data [datetime64]
        variable: data to be average
        minpts: minimum number of points needed for a valid value, else filled with nan
        tFreq: the spacing between centered averages in Days, default window size = tFreq*2
        """
        tsmin = pd.Timestamp(np.min(mid_dates))
        tsmax = pd.Timestamp(np.max(mid_dates))
        ts = pd.date_range(start=tsmin, end=tsmax, freq=f"{tFreq}D")
        ts = pd.to_datetime(ts).values
        idx0 = ~np.isnan(variable)
        runmean = np.empty([len(ts) - 1, 1])
        runmean[:] = np.nan
        tsmean = ts[0:-1]

        t_np = mid_dates.astype(np.int64)

        for i in range(len(ts) - 1):
            idx = (
                (mid_dates >= (ts[i] - np.timedelta64(int(tFreq / 2), "D")))
                & (mid_dates < (ts[i + 1] + np.timedelta64(int(tFreq / 2), "D")))
                & idx0
            )
            if sum(idx) >= minpts:
                runmean[i] = np.mean(variable[idx])
                tsmean[i] = np.mean(t_np[idx])

        tsmean = pd.to_datetime(tsmean).values
        return (runmean, tsmean)

    def add_point(self, coordinates):
        color = plt.cm.tab10(self.icon_color_index)
        if self.config["verbose"]:
            print(self.icon_color_index, color)
        html_for_marker = f"""
        <div>
            <h1 style="position: absolute;left: -0.2em; top: -2.5rem; font-size: 2rem;">
            <span style="color: rgba({color[0]*100}%,{color[1]*100}%,{color[2]*100}%, {color[3]});
                width: 2rem;height: 2rem; display: block;position: relative;transform: rotate(45deg);">
                <strong>+</strong>
            </span>
            </h1>
        </div>
        """

        icon = ipyleaflet.DivIcon(
            html=html_for_marker, icon_anchor=[0, 0], icon_size=[0, 0]
        )
        new_point = ipyleaflet.Marker(location=coordinates, icon=icon)

        # added points are tracked (color/symbol assigned) by the order they are added to the layer_group
        # (each point/icon is a layer by itself in ipyleaflet)
        self._map_picked_points_layer_group.add_layer(new_point)

        if self.config["verbose"]:
            print(f"point added {coordinates}")
        self.icon_color_index += 1

    def _handle_map_click(self, **kwargs):
        if kwargs.get("type") == "click":
            coords = kwargs.get("coordinates")
            # NOTE this is the work around for the double click issue discussed above!
            # Only acknoledge the click when it is registered the second time at the same place!
            if self.config["coords"] is not None:
                print(kwargs.get("coordinates"))
                self.config["coords"]["latitude"].value = round(coords[0], 2)
                self.config["coords"]["longitude"].value = round(coords[1], 2)
            if self._last_click and (
                kwargs.get("coordinates") == self._last_click.get("coordinates")
            ):
                self.add_point(coords)
            else:
                print(kwargs.get("type"))
                self._last_click = kwargs

    def _plot_by_satellite(self, ins3xr, point_v, point_xy, map_epsg):

        try:
            sat = np.array([x[0] for x in ins3xr["satellite_img1"].values])
        except Exception:
            sat = np.array([str(int(x)) for x in ins3xr["satellite_img1"].values])

        sats = np.unique(sat)
        sat_plotsym_dict = {
            "1": "r+",
            "2": "bo",
            "4": "y+",
            "5": "y+",
            "7": "c+",
            "8": "g*",
            "9": "m^",
        }

        sat_label_dict = {
            "1": "Sentinel 1",
            "2": "Sentinel 2",
            "4": "Landsat 4",
            "5": "Landsat 5",
            "7": "Landsat 7",
            "8": "Landsat 8",
            "9": "Landsat 9",
        }

        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Speed (m/yr)")
        self.ax.set_title("ITS_LIVE Ice Flow Speed m/yr")

        max_dt = self.config["max_separation_days"]
        min_dt = self.config["min_separation_days"]
        dt = ins3xr["date_dt"].values
        # TODO: document this
        dt = dt.astype(float) * 1.15741e-14
        if "running_mean" in self.config and self.config["running_mean"]:
            runmean, ts = self.runningMean(
                ins3xr.mid_date[(dt >= min_dt) & (dt <= max_dt)].values,
                point_v[(dt >= min_dt) & (dt <= max_dt)].values,
                5,
                30,
            )
            self.ax.plot(
                ts,
                runmean,
                linestyle="-",
                color=plt.cm.tab10(self.color_index),
                linewidth=2,
            )

        for satellite in sats[::-1]:
            if any(sat == satellite):
                self.ax.plot(
                    ins3xr["mid_date"][
                        (sat == satellite) & (dt >= min_dt) & (dt <= max_dt)
                    ],
                    point_v[(sat == satellite) & (dt >= min_dt) & (dt <= max_dt)],
                    sat_plotsym_dict[satellite],
                    markersize=3,
                    label=sat_label_dict[satellite],
                )

    def _plot_by_points(self, ins3xr, point_v, point_xy, map_epsg):
        point_label = f"Lat: {round(point_xy[1], 2)}, Lon: {round(point_xy[0], 2)}"
        if self.config["verbose"]:
            print(point_xy)

        dt = ins3xr["date_dt"].values
        # TODO: document this
        dt = dt.astype(float) * 1.15741e-14

        max_dt = self.config["max_separation_days"]
        min_dt = self.config["min_separation_days"]
        # set the maximum image-pair time separation (dt) that will be plotted
        alpha_value = 0.75
        marker_size = 3
        if "running_mean" in self.config and self.config["running_mean"]:
            alpha_value = 0.25
            marker_size = 2
            runmean, ts = self.runningMean(
                ins3xr.mid_date[(dt >= min_dt) & (dt <= max_dt)].values,
                point_v[(dt >= min_dt) & (dt <= max_dt)].values,
                5,
                30,
            )
            self.ax.plot(
                ts,
                runmean,
                linestyle="-",
                color=plt.cm.tab10(self.color_index),
                linewidth=2,
            )
        self.ax.plot(
            ins3xr.mid_date[(dt >= min_dt) & (dt <= max_dt)],
            point_v[(dt >= min_dt) & (dt <= max_dt)],
            linestyle="None",
            markeredgecolor=plt.cm.tab10(self.color_index),
            markerfacecolor=plt.cm.tab10(self.color_index),
            marker="o",
            alpha=alpha_value,
            markersize=marker_size,
            label=point_label,
        )

    def plot_point_on_fig(self, point_xy, map_epsg):

        # pointxy is [x,y] coordinate in mapfig projection (map_epsg below), nax is plot axis for time series plot
        start = time.time()
        if self.config["verbose"]:
            print(
                f"fetching timeseries for point x={point_xy[0]:10.2f} y={point_xy[1]:10.2f}",
                flush=True,
            )
        if "plot" in self.config:
            variable = self.config["plot"]
        else:
            variable = "v"

        ins3xr, ds_point, point_tilexy = self.dct.get_timeseries_at_point(
            point_xy, map_epsg, variables=[variable]
        )
        if ins3xr is not None:
            export = ins3xr[
                [
                    "v",
                    "v_error",
                    "vx",
                    "vx_error",
                    "vy",
                    "vy_error",
                    "date_dt",
                    "satellite_img1",
                    "mission_img1",
                ]
            ].sel(x=point_tilexy[0], y=point_tilexy[1], method="nearest")

            self.ts.append((export, point_xy))
            ds_velocity_point = ds_point[variable]
            # dct.get_timeseries_at_point returns dataset, extract dataArray for variable from it for plotting
            # returns xarray dataset object (used for time axis in plot) and already loaded v time series

            if self.config["color_by"] == "satellite":
                self._plot_by_satellite(ins3xr, ds_velocity_point, point_xy, map_epsg)
            else:
                self._plot_by_points(ins3xr, ds_velocity_point, point_xy, map_epsg)
            plt.tight_layout()
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            plt.legend(
                by_label.values(), by_label.keys(), loc="upper left", fontsize=10
            )
            total_time = time.time() - start
            if self.config["verbose"]:
                print(
                    f"elapsed time: {total_time:10.2f} - {len(ds_velocity_point)/total_time:6.1f} points per second",
                    flush=True,
                )
            self.color_index += 1

    def export_data(self, *args, **kwargs):
        dir_name = uuid4()
        directory = Path(f"data/{dir_name}/series")
        directory.mkdir(parents=True, exist_ok=True)

        for time_series in self.ts:
            # time_series[0].load()
            lat = round(time_series[1][1], 4)
            lon = round(time_series[1][0], 4)
            df = time_series[0].to_dataframe()
            df["x"] = lon
            df["y"] = lat
            df = df.rename(
                columns={
                    "x": "lon",
                    "y": "lat",
                    "satellite_img1": "satellite",
                    "mission_img1": "mission",
                    "v": "v [m/yr]",
                    "v_error": "v_error [m/yr]",
                    "vx": "vx [m/yr]",
                    "vx_error": "vx_error [m/yr]",
                    "vy": "vy [m/yr]",
                    "vy_error": "vy_error [m/yr]",
                }
            )
            ts = df.dropna()
            ts["epsg"] = time_series[0].attrs["projection"]
            ts["date_dt [days]"] = ts["date_dt"].dt.days
            file_name = f"LAT{lat}--LON{lon}.csv"
            ts.to_csv(
                f"data/{dir_name}/series/{file_name}",
                columns=[
                    "lat",
                    "lon",
                    "v [m/yr]",
                    "v_error [m/yr]",
                    "vx [m/yr]",
                    "vx_error [m/yr]",
                    "vy [m/yr]",
                    "vy_error [m/yr]",
                    "date_dt [days]",
                    "mission",
                    "satellite",
                    "epsg",
                ],
            )

        with zipfile.ZipFile(
            f"data/{dir_name}/itslive-data.zip", "w", zipfile.ZIP_DEFLATED
        ) as zip_file:
            for entry in directory.rglob("*"):
                zip_file.write(entry, entry.relative_to(directory))

        shutil.rmtree(f"data/{dir_name}/series")
        if self.config["data_link"]:
            self.config[
                "data_link"
            ].value = f"""
            <a target="_blank" href="data/{dir_name}/itslive-data.zip" >
                <div class="jupyter-button mod-warning">Download Data</div>
            </a>
            """

    def plot_time_series(self, *args, **kwargs):

        # reset plot and color index
        self.ax.clear()
        self.ax.set_xlabel("date")
        self.ax.set_ylabel("speed (m/yr)")
        self.fig.tight_layout()
        self.color_index = 0
        self.ts = []

        picked_points_latlon = [
            a.location for a in self._map_picked_points_layer_group.layers
        ]
        if len(picked_points_latlon) > 0:
            self.ax.set_title("Plotting...")
            self.fig.canvas.draw()
            self._control_plot_button.disabled = True
            if self.config["verbose"]:
                print("Plotting...")
            for lat, lon in picked_points_latlon:
                self.plot_point_on_fig([lon, lat], "4326")
            if self.config["verbose"]:
                print("done plotting")
            plt.get_current_fig_manager().canvas.set_window_title("")
            self.ax.set_title("ITS_LIVE Ice Flow Speed m/yr")
            self.fig.canvas.draw()

            self._control_plot_button.disabled = False
            # plt.show()
        else:
            print("no picked points to plot yet - pick some!")

    def clear_points(self, *args, **kwargs):
        self.ax.clear()
        self.color_index = 0
        self.icon_color_index = 0
        self._map_picked_points_layer_group.clear_layers()
        print("all points cleared")
