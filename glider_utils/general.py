import re
import logging
from datetime import datetime as dt
from dateutils.parser import parser as dtparse
import numpy as np
import pandas as pd
from glider_utils.parsers.dbd_parsers import get_fileopen_time


def mts(timestr):
    """returns a unix timestamp in seconds since Jan 1, 1970"""
    ts = dtparse(timestr)
    return (ts - datetime(1970,1,1)).total_seconds()
    
def ooimts(timestr):
    """returns a unix timestamp in milliseconds since Jan 1 1970"""
    return int(mts(timestr) * 1000)

def gdpath(glider, deployment):
    """returns the path to a specific glider deployment data directory"""
    pass
    
def gliderfile_from_time(ts, files):
    """the glider data file that includes a time
    
    Parameters
    ----------
    ts : int, float, datetime object, pandas datetime, or datetime string
        the represented timestamp to look for
    files : list
        the list of files to search through.
    """
    if isinstance(ts, str):
        ts = dtparse(ts)
    elif isinstance(ts, (int, float)):
        ts = dt.utcfromtimestamp(ts)
    #elif isinstance(ts, dt):
    opentimes = np.empty(len(files), dtype='datetime64[ns]')
    for ii, file in enumerate(files):
        opentime = get_fileopen_time(file)
        ot_dt = dt.strptime(opentime.replace("_", " "), "%c")
        opentimes[ii] = ot_dt
    # get the sorting indices
    sortii = np.argsort(opentimes)
    sorted_ots = opentimes[sortii]
    sorted_files = np.array(files)[sortii]
    
    file_index = np.flatnonzero(sorted_ots < timex)[-1]
    return sorted_files[file_index]

slocumregex = (
    r'[a-z_0-9]+(?:_|-)(\d{4}(?:_|-)\d{3}(?:_|-))(\d{1,2})(?:_|-)'
    r'(\d{1,4})\..+')
regex = re.compile(slocumregex)


def sort_function(filename):
    fname = os.path.basename(filename)
    match = regex.search(fname)
    if not match:
        error_msg = (
            'File {:s} does not match the Slocum filename format.'.format(
                filename
            ))
        logging.warning(error_msg)
        raise ValueError(error_msg)
    else:
        mission_num = '{:02d}'.format(int(match.group(2)))
        segment_num = '{:04d}'.format(int(match.group(3)))
        sort_str = match.group(1) + mission_num + '_' + segment_num
    return sort_str