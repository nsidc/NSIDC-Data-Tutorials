#----------------------------------------------------------------------
# Functions for snow tutorial notebooks
#
# In Python a module is just a collection of functions in a file with
# a .py extension.
#
# Functions are defined using:
#
# def function_name(argument1, arguments2,... keyword_arg1=some_variable) 
#     '''A docstring explaining what the function does and what
#        arguments it expectes.
#     '''
#     <commands>
#     return some_value  # Not required unless you need to return a value
#
#----------------------------------------------------------------------

import h5py
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gpd
from datetime import datetime, timedelta
import pyproj
import requests
import json
from statistics import mean
from xml.etree import ElementTree as ET
import os
import pprint
import shutil
import zipfile
import io
import time
import itertools
from urllib.parse import urlparse
import netrc
import base64
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
import getpass


def granule_info(data_dict):
    '''
    Prints number of granules based on inputted data set short name, version, bounding box, and temporal range. Queries the CMR and pages over results.
    
    data_dict - a dictionary with the following CMR keywords:
    'short_name',
    'version',
    'bounding_box',
    'temporal'
    '''
    # set CMR API endpoint for granule search
    granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'
    
    # add page size and page num to dictionary
    data_dict['page_size'] = 2000
    data_dict['page_num'] = 1
    
    granules = []
    headers={'Accept': 'application/json'}
    while True:
        response = requests.get(granule_search_url, params=data_dict, headers=headers)
        results = json.loads(response.content)

        if len(results['feed']['entry']) == 0:
            # Out of results, so break out of loop
            data_dict['page_num'] -= 1
            break

        # Collect results and increment page_num
        granules.extend(results['feed']['entry'])
        data_dict['page_num'] += 1
    
    # calculate granule size 
    granule_sizes = [float(granule['granule_size']) for granule in granules]
    print('There are', len(granules), 'files of', data_dict['short_name'], 'version', data_dict['version'], 'over my area and time of interest.')
    print(f'The average size of each file is {mean(granule_sizes):.2f} MB and the total size of all {len(granules)} granules is {sum(granule_sizes):.2f} MB')
    return len(granules)

def merge_intervals(intervals):
    sorted_by_lower_bound = sorted(intervals, key=lambda tup: tup[0])
    merged = []
    for higher in sorted_by_lower_bound:
        if not merged:
            merged.append(higher)
        else:
            lower = merged[-1]
            # test for intersection between lower and higher:
            # we know via sorting that lower[0] <= higher[0]
            if higher[0] <= lower[1]:
                upper_bound = max(lower[1], higher[1])
                merged[-1] = (lower[0], upper_bound)  # replace by merged interval
            else:
                merged.append(higher)
    return merged


def time_overlap(data_dict):
    '''
    Prints dataframe with file names, dataset_id, start date, and end date for all files that overlap in temporal range across all data sets in dictionary
    
    data_dict - a dictionary with the following CMR keywords:
    'short_name',
    'version',
    'bounding_box',
    'temporal'
    '''
    # set CMR API endpoint for granule search
    granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'
    headers= {'Accept': 'application/json'}
    
    # Create dataframe with identifiers and temporal ranges
    granules = []
    column_names = ['dataset_id', 'short_name','version', 'producer_granule_id', 'start_date', 'end_date']
    df = pd.DataFrame(columns = column_names)
    for k, v in data_dict.items(): 
        # add page size and page num to dictionary
        data_dict[k]['page_size'] = 2000
        data_dict[k]['page_num'] = 1

        while True:
            response = requests.get(granule_search_url, params=data_dict[k], headers=headers)
            results = json.loads(response.content)
            if len(results['feed']['entry']) == 0:
                # Out of results, so break out of loop
                data_dict[k]['page_num'] -= 1
                break
            # Collect results and increment page_num
            granules.extend(results['feed']['entry'])
            data_dict[k]['page_num'] += 1
        # compile lists from granule metadata
        dataset_id = [granule['dataset_id'] for granule in granules]
        title = [granule['title'] for granule in granules]
        producer_granule_id = [granule['producer_granule_id'] for granule in granules]
        start_date = [granule['time_start'] for granule in granules]
        end_date = [granule['time_end'] for granule in granules]

    # split title to feed short_name and version lists 
    title_split = [i.split(':') for i in title]
    name = [i[1] for i in title_split]
    name_split = [i.split('.') for i in name]

    df['dataset_id'] = dataset_id
    df['short_name'] = [i[0] for i in name_split]
    df['version'] = [i[1] for i in name_split]
    df['producer_granule_id'] = producer_granule_id
    df['start_date'] = start_date
    df['end_date'] = end_date
    
    # Convert state time to integers 
    df['start_int'] = pd.DatetimeIndex(df['start_date']).astype(np.int64)
    df['end_int'] = pd.DatetimeIndex(df['end_date']).astype(np.int64)
    
    merged = merge_intervals(zip(df['start_int'], df['end_int']))
    df['overlap_group'] = df['start_int'].apply(lambda x: next(i for i, m in enumerate(merged) if m[0] <= x <= m[1]))
    
    # Find each unique value in overlap_group
    len_datasets = len(df.dataset_id.unique())
    len_groups = len(df.overlap_group.unique())
    unique_group = list(df.overlap_group.unique())

    # Loop over each overlap group
    tempdf = df.copy()
    
    for i in range(len_groups):
        tempdf = df.copy()
        # Filter rows corresponding to unique_group value
        filter_df = tempdf.loc[tempdf['overlap_group'] == unique_group[i]]  
        # If not all datasets exist, remove this group from our main tempdf
        filter_len_datasets = len(filter_df.dataset_id.unique())
        if filter_len_datasets < len_datasets: df = df.loc[df.overlap_group != unique_group[i]]
    
    df = df.drop(columns=['start_int', 'end_int', 'overlap_group'])
    return df

def get_username():
    username = ''

    # For Python 2/3 compatibility:
    try:
        do_input = raw_input  # noqa
    except NameError:
        do_input = input

    while not username:
        try:
            username = do_input('Earthdata username: ')
        except KeyboardInterrupt:
            quit()
    return username


def get_password():
    password = ''
    while not password:
        try:
            password = getpass('password: ')
        except KeyboardInterrupt:
            quit()
    return password

def get_credentials(url):
    URS_URL = 'https://urs.earthdata.nasa.gov'
    """Get user credentials from .netrc or prompt for input."""
    credentials = None
    errprefix = ''
    try:
        info = netrc.netrc()
        username, account, password = info.authenticators(urlparse(URS_URL).hostname)
        errprefix = 'netrc error: '
    except Exception as e:
        if (not ('No such file' in str(e))):
            print('netrc error: {0}'.format(str(e)))
        username = None
        password = None

    while not credentials:
        if not username:
            username = get_username()
            password = get_password()
        credentials = '{0}:{1}'.format(username, password)
        credentials = base64.b64encode(credentials.encode('ascii')).decode('ascii')

        if url:
            try:
                req = Request(url)
                req.add_header('Authorization', 'Basic {0}'.format(credentials))
                opener = build_opener(HTTPCookieProcessor())
                opener.open(req)
            except HTTPError:
                print(errprefix + 'Incorrect username or password')
                errprefix = ''
                credentials = None
                username = None
                password = None

    return credentials

def cmr_filter_urls(search_results):
    """Select only the desired data files from CMR response."""
    if 'feed' not in search_results or 'entry' not in search_results['feed']:
        return []

    entries = [e['links']
               for e in search_results['feed']['entry']
               if 'links' in e]
    # Flatten "entries" to a simple list of links
    links = list(itertools.chain(*entries))

    urls = []
    unique_filenames = set()
    for link in links:
        if 'href' not in link:
            # Exclude links with nothing to download
            continue
        if 'inherited' in link and link['inherited'] is True:
            # Why are we excluding these links?
            continue
        if 'rel' in link and 'data#' not in link['rel']:
            # Exclude links which are not classified by CMR as "data" or "metadata"
            continue
        if 'title' in link and 'opendap' in link['title'].lower():
            # Exclude OPeNDAP links--they are responsible for many duplicates
            # This is a hack; when the metadata is updated to properly identify
            # non-datapool links, we should be able to do this in a non-hack way
            continue

        filename = link['href'].split('/')[-1]
        if filename in unique_filenames:
            # Exclude links with duplicate filenames (they would overwrite)
            continue
        unique_filenames.add(filename)

        urls.append(link['href'])

    return urls

def build_cmr_query_url(short_name, version, time_start, time_end,
                        bounding_box=None, polygon=None,
                        filename_filter=None):
    params = '&short_name={0}'.format(short_name)
    params += version
    params += '&temporal[]={0},{1}'.format(time_start, time_end)
    if polygon:
        params += '&polygon={0}'.format(polygon)
    elif bounding_box:
        params += '&bounding_box={0}'.format(bounding_box)
    if filename_filter:
        option = '&options[producer_granule_id][pattern]=true'
        params += '&producer_granule_id[]={0}{1}'.format(filename_filter, option)
    return CMR_FILE_URL + params

def cmr_download(urls):
    """Download files from list of urls."""
    URS_URL = 'https://urs.earthdata.nasa.gov'
    if not urls:
        return

    url_count = len(urls)
    print('Downloading {0} files...'.format(url_count))
    credentials = None

    for index, url in enumerate(urls, start=1):
        if not credentials and urlparse(url).scheme == 'https':
            credentials = get_credentials(url)

        filename = url.split('/')[-1]
        filename = (filename[:255]) if len(filename) > 255 else filename
        print('{0}/{1}: {2}'.format(str(index).zfill(len(str(url_count))),
                                    url_count,
                                    filename))

        try:
            # In Python 3 we could eliminate the opener and just do 2 lines:
            # resp = requests.get(url, auth=(username, password))
            # open(filename, 'wb').write(resp.content)
            req = Request(url)
            if credentials:
                req.add_header('Authorization', 'Basic {0}'.format(credentials))
            opener = build_opener(HTTPCookieProcessor())
            data = opener.open(req).read()
            open(filename, 'wb').write(data)
        except HTTPError as e:
            print('HTTP error {0}, {1}'.format(e.code, e.reason))
        except URLError as e:
            print('URL error: {0}'.format(e.reason))
        except IOError:
            raise
        except KeyboardInterrupt:
            quit()


def print_service_options(data_dict, response):
    '''
    Prints the available subsetting, reformatting, and reprojection services available based on inputted data set name, version, and Earthdata Login username and       password. 
    
    data_dict - a dictionary with the following keywords:
    'short_name',
    'version',
    'uid',
    'pswd'
    '''

    root = ET.fromstring(response.content)

    #collect lists with each service option
    subagent = [subset_agent.attrib for subset_agent in root.iter('SubsetAgent')]

    # variable subsetting
    variables = [SubsetVariable.attrib for SubsetVariable in root.iter('SubsetVariable')]  
    variables_raw = [variables[i]['value'] for i in range(len(variables))]
    variables_join = [''.join(('/',v)) if v.startswith('/') == False else v for v in variables_raw] 
    variable_vals = [v.replace(':', '/') for v in variables_join]

    # reformatting
    formats = [Format.attrib for Format in root.iter('Format')]
    format_vals = [formats[i]['value'] for i in range(len(formats))]
    if format_vals : format_vals.remove('')

    # reprojection options
    projections = [Projection.attrib for Projection in root.iter('Projection')]
    proj_vals = []
    for i in range(len(projections)):
        if (projections[i]['value']) != 'NO_CHANGE' :
            proj_vals.append(projections[i]['value'])

    #print service information depending on service availability and select service options
    print('Services available for', data_dict['short_name'],':')
    print()
    if len(subagent) < 1 :
            print('No customization services available.')
    else:
        subdict = subagent[0]
        if subdict['spatialSubsetting'] == 'true':
            print('Bounding box subsetting')
        if subdict['spatialSubsettingShapefile'] == 'true':
            print('Shapefile subsetting')
        if subdict['temporalSubsetting'] == 'true':
            print('Temporal subsetting')
        if len(variable_vals) > 0:
            print('Variable subsetting')
        if len(format_vals) > 0 :
            print('Reformatting to the following options:', format_vals)
        if len(proj_vals) > 0 : 
            print('Reprojection to the following options:', proj_vals)

    

            
def request_data(param_dict,session):
    '''
    Request data from NSIDC's API based on inputted key-value-pairs from param_dict. 
    Different request methods depending on 'async' or 'sync' options.
    
    In addition to param_dict, input Earthdata login `uid` and `pswd`.
    '''
    
    # Create an output folder if the folder does not already exist.
    path = str(os.getcwd() + '/Outputs')
    if not os.path.exists(path):
        os.mkdir(path)

    # Define base URL
    base_url = 'https://n5eil02u.ecs.nsidc.org/egi/request'
    
    # Different access methods depending on request mode:

    if param_dict['request_mode'] == 'async':
        request = session.get(base_url, params=param_dict)
        print('Request HTTP response: ', request.status_code)

        # Raise bad request: Loop will stop for bad response code.
        request.raise_for_status()
        print()
        print('Order request URL: ', request.url)
        print()
        esir_root = ET.fromstring(request.content)
        #print('Order request response XML content: ', request.content)

        #Look up order ID
        orderlist = []   
        for order in esir_root.findall("./order/"):
            orderlist.append(order.text)
        orderID = orderlist[0]
        print('order ID: ', orderID)

        #Create status URL
        statusURL = base_url + '/' + orderID
        print('status URL: ', statusURL)

        #Find order status
        request_response = session.get(statusURL)    
        print('HTTP response from order response URL: ', request_response.status_code)

        # Raise bad request: Loop will stop for bad response code.
        request_response.raise_for_status()
        request_root = ET.fromstring(request_response.content)
        statuslist = []
        for status in request_root.findall("./requestStatus/"):
            statuslist.append(status.text)
        status = statuslist[0]
        #print('Data request is submitting...')
        print()
        print('Initial request status is ', status)
        print()

        #Continue loop while request is still processing
        loop_response = session.get(statusURL)
        loop_root = ET.fromstring(loop_response.content)
        while status == 'pending' or status == 'processing': 
            print('Status is not complete. Trying again.')
            time.sleep(10)
            loop_response = session.get(statusURL)

            # Raise bad request: Loop will stop for bad response code.
            loop_response.raise_for_status()
            loop_root = ET.fromstring(loop_response.content)

            #find status
            statuslist = []
            for status in loop_root.findall("./requestStatus/"):
                statuslist.append(status.text)
            status = statuslist[0]
            print('Retry request status is: ', status)
            if status == 'pending' or status == 'processing':
                continue

        #Order can either complete, complete_with_errors, or fail:
        # Provide complete_with_errors error message:
        if status == 'failed':
            messagelist = []
            for message in loop_root.findall("./processInfo/"):
                messagelist.append(message.text)
            print('error messages:')
            pprint.pprint(messagelist)
            print()

        # Download zipped order if status is complete or complete_with_errors
        if status == 'complete' or status == 'complete_with_errors':
            downloadURL = 'https://n5eil02u.ecs.nsidc.org/esir/' + orderID + '.zip'
            print('Zip download URL: ', downloadURL)
            print('Beginning download of zipped output...')
            zip_response = session.get(downloadURL)
            # Raise bad request: Loop will stop for bad response code.
            zip_response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                z.extractall(path)
            print('Data request is complete.')
        else: print('Request failed.')

    else:
        print('Requesting...')
        request = session.get(s.url,auth=(uid,pswd))
        print('HTTP response from order response URL: ', request.status_code)
        request.raise_for_status()
        d = request.headers['content-disposition']
        fname = re.findall('filename=(.+)', d)
        dirname = os.path.join(path,fname[0].strip('\"'))
        print('Downloading...')
        open(dirname, 'wb').write(request.content)
        print('Data request is complete.')

        # Unzip outputs
        for z in os.listdir(path): 
            if z.endswith('.zip'): 
                zip_name = path + "/" + z 
                zip_ref = zipfile.ZipFile(zip_name) 
                zip_ref.extractall(path) 
                zip_ref.close() 
                os.remove(zip_name)             

                
def clean_folder():
    '''
    Cleans up output folder by removing individual granule folders. 
    
    '''
    path = str(os.getcwd() + '/Outputs')
    
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            try:
                shutil.move(os.path.join(root, file), path)
            except OSError:
                pass
        for name in dirs:
            os.rmdir(os.path.join(root, name))    
            
            
def load_icesat2_as_dataframe(filepath, VARIABLES):
    '''
    Load points from an ICESat-2 granule 'gt<beam>' groups as DataFrame of points. Uses VARIABLES mapping
    to select subset of '/gt<beam>/...' variables  (Assumes these variables share dimensions)
    Arguments:
        filepath to ATL0# granule
    '''
    
    ds = h5py.File(filepath, 'r')

    # Get dataproduct name
    dataproduct = ds.attrs['identifier_product_type'].decode()
    # Convert variable paths to 'Path' objects for easy manipulation
    variables = [Path(v) for v in VARIABLES[dataproduct]]
    # Get set of beams to extract individially as dataframes combining in the end
    beams = {list(v.parents)[-2].name for v in variables}
    
    dfs = []
    for beam in beams:
        data_dict = {}
        beam_variables = [v for v in variables if beam in str(v)]
        for variable in beam_variables:
            # Use variable 'name' as column name. Beam will be specified in 'beam' column
            column = variable.name
            variable = str(variable)
            try:
                values = ds[variable][:]
                # Convert invalid data to np.nan (only for float columns)
                if 'float' in str(values.dtype):
                    if 'valid_min' in ds[variable].attrs:
                        values[values < ds[variable].attrs['valid_min']] = np.nan
                    if 'valid_max' in ds[variable].attrs:
                        values[values > ds[variable].attrs['valid_max']] = np.nan
                    if '_FillValue' in ds[variable].attrs:
                        values[values == ds[variable].attrs['_FillValue']] = np.nan
                    
                data_dict[column] = values
            except KeyError:
                print(f'Variable {variable} not found in {filepath}. Likely an empty granule.')
                raise
                
        df = pd.DataFrame.from_dict(data_dict)
        df['beam'] = beam
        dfs.append(df)
        
    df = pd.concat(dfs, sort=True)
    # Add filename column for book-keeping and reset index
    df['filename'] = Path(filepath).name
    df = df.reset_index(drop=True)
    
    return df



def convert_to_gdf(df):
    '''
    Converts a DataFrame of points with 'longitude' and 'latitude' columns to a
    GeoDataFrame
    '''
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs={'init': 'epsg:4326'},
    )

    return gdf


def convert_delta_time(delta_time):
    '''
    Convert ICESat-2 'delta_time' parameter to UTC datetime
    '''
    EPOCH = datetime(2018, 1, 1, 0, 0, 0)
    
    utc_datetime = EPOCH + timedelta(seconds=delta_time)

    return utc_datetime


# def compute_distance(df):
#     '''
#     Calculates along track distance for each point within the 'gt1l', 'gt2l', and 'gt3l' beams, beginning with first beam index. 

#     Arguments:
#         df: DataFrame with icesat-2 data

#     Returns:
#         add_dist added as new column to initial df
#     '''

#     beam_1 = df[df['beam'] == 'gt1l']
#     beam_2 = df[df['beam'] == 'gt2l']
#     beam_3 = df[df['beam'] == 'gt3l']

#     add_dist = []
#     add_dist.append(beam_1.height_segment_length_seg.values[0])

#     for i in range(1, len(beam_1)): 
#         add_dist.append(add_dist[i-1] + beam_1.height_segment_length_seg.values[i])

#     add_dist_se = pd.Series(add_dist)
#     beam_1.insert(loc=0, column='add_dist', value=add_dist_se.values)
#     beam_1

#     add_dist = []
#     add_dist.append(beam_2.height_segment_length_seg.values[0])

#     for i in range(1, len(beam_2)): 
#         add_dist.append(add_dist[i-1] + beam_2.height_segment_length_seg.values[i])

#     add_dist_se = pd.Series(add_dist)
#     beam_2.insert(loc=0, column='add_dist', value=add_dist_se.values)
#     beam_2

#     add_dist = []
#     add_dist.append(beam_3.height_segment_length_seg.values[0])

#     for i in range(1, len(beam_3)): 
#         add_dist.append(add_dist[i-1] + beam_3.height_segment_length_seg.values[i])

#     add_dist_se = pd.Series(add_dist)
#     beam_3.insert(loc=0, column='add_dist', value=add_dist_se.values)
#     beam_3

#     beams = [beam_1,beam_2,beam_3]
#     df = pd.concat(beams,ignore_index=True)
    
#     return df
