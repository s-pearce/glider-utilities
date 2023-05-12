import pandas as pd
from datetime import datetime as dt
from dateutils.parser import parser as dtparse
import numpy as np
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
    elif isinstance(ts, dt):
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