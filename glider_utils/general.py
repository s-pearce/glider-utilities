import pandas as pd
from datetime import datetime

def mts(timestr):
    """returns a unix timestamp in seconds since Jan 1, 1970"""
    ts = pd.to_datetime(timestr)
    return (ts - datetime(1970,1,1)).total_seconds()
    
def ooimts(timestr):
    """returns a unix timestamp in milliseconds since Jan 1 1970"""
    return int(mts(timestr) * 1000)

def gdpath(glider, deployment):
    """returns the path to a specific glider deployment data directory"""
    pass