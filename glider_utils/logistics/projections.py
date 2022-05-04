from datetime import datetime as dt
from datetime import timedelta as td
import pandas as pd

def calc_distance_travel_by(
        end_datetime, speed, lastpos_datetime, 
        speedunits="m/s", distunits="nm"):
    """
    """
    pti = pd.to_datetime(lastpos_datetime)
    ptf = pd.to_datetime(end_datetime)
    seconds_elapsed = pti
    
    
    