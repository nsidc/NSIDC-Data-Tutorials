FROM jupyter/base-notebook:python-3.7.3

USER root

# Install all OS dependencies for notebook server that starts but lacks all
# features (e.g., download as all possible file formats)
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update \
 && apt-get install -yq --no-install-recommends git \
 && apt-get clean  && apt autoremove && rm -rf /var/lib/apt

USER $NB_UID

RUN conda install -c conda-forge --quiet --yes --freeze-installed \
'matplotlib=3.1.1' \
'descartes=1.1.0' \
'pandas=0.24.2' \
'cartopy=0.17.0' \
'fiona=1.8.4' \
'shapely=1.6.4' \
'geopandas=0.7.0' \
'h5py=2.9.0' \
'requests=2.22.0' \
'plotly=4.0.0' \
'geopy=1.20.0' \
'xarray=0.14.0' \
'pyresample=1.13.2' \
'hvplot=0.5.2' \
'awscli=1.16.296' \
'rasterio=1.1.1' \
'holoviews=1.12.7' \
'netcdf4=1.5.3' && \
conda clean --yes --all  && \
npm cache clean --force && \
rm -rf /opt/conda/lib/python3.7/site-packages/awscli/examples \
&& find /opt/conda/ -follow -type f -name '*.a' -delete \
&& find /opt/conda/ -follow -type f -name '*.pyc' -delete \
&& find /opt/conda/ -follow -type f -name '*.js.map' -delete \
&& find /opt/conda/lib/python*/site-packages/bokeh/server/static -follow -type f -name '*.js' ! -name '*.min.js' -delete

RUN fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

USER $NB_UID
