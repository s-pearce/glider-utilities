#! python
# a function to gather glider amphrs per day for the average over each day

from datetime import datetime as dt
from datetime import timedelta as td
import pandas as pd
import numpy as np


def amphrs_used_per_day(pdts, amphrs):
    """ calculate each day's amp hours used as a rate amphrs/day
    
    Parameters
    ----------
    pdts : pandas DatetimeIndex
        The time stamps corresponding to `amphrs`
    amphrs : numpy ndarray
        A glider's measured cumulative amp hours used from 
        `m_coulomb_amphr_total`.  Should have NaNs removed already.
        
    Returns
    -------
    ahrs_timestamps : pandas DatetimeIndex
        A timestamp array with timestamps centered on UTC noon for each 
        day's amphr rate calculated.  If the last day of the `amphrs` 
        input ends before UTC noon, it keeps the
    ahrsperday : numpy 1-D array
        The amp hours per day rate for each day from the input data.
    
    """
    # get the bounds
    start = pdts[0]
    end = pdts[-1]
    # need each day without time for finding the day's data indexes
    # so create a daterange (no times)
    daterange = pd.date_range(start.date(), end.date())
    
    # find the amphrs used each day as an amphrs_per_day value
    ahrspd = []
    ahrspd_ts = []
    for dayte in daterange:
        day_ii = np.flatnonzero(pdts.date == dayte)  # the day's indices
        if len(day_ii) == 0:
            continue
        ahrs_used = amphrs[day_ii][-1] - amphrs[day_ii][0]
        day_fraction = (pdts[day_ii][-1] - pdts[day_ii][0]).total_seconds() / 86400
        ahrs_per_day = ahrs_used / day_fraction
        ahrspd.append(ahrs_per_day)
        ahrspd_ts.append(dayte)
    
        # for plotting amphrs per day create a timestamp for each value at
    # the day's center.
    ahrspd_ts = ahrspd_ts + td(hours=12)
    # If the last timestamps of data is less than the day center (12:00 UTC)
    # then make the last timestamp the same as the end of the data record
    if ahrspd_ts[-1] > pdts[-1]:
        ahrspd_ts = ahrspd_ts[:-1].append(pd.DatetimeIndex([pdts[-1]]))

    return ahrspd_ts, np.array(ahrspd)
    