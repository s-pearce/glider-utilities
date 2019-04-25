#! /cygdrive/c/Users/spearce/Anaconda3/python
import os
import sys
import pdb
import logging
import datetime as dt
import pickle

import netCDF4
import numpy as np

sys.path.append('C:\\Users\\spearce\\code\\python\\gliderdac')
from ooidacutils.ooi_gps import iso2deg
from fwd_fill_and_cluster_find import fwd_fill

"""days_of_gldata.py  Number of days of chlorophyll data on the GH & NH line.

This code is to determine the number of days of chlorophyll data available on
the 2 principal OOI CE glider lines off of the Washington coast, the Gray's
Harbor (GH) line, and off the Oregon coast, the Newport Hydrographic (NH) line.

These lines are primarily zonal and are defined in this code by an upper &
lower latitude boundary.

The GH line is defined by latitude bounds: 46° 45.0' N to 47° 15.5' N
The NH line is defined by latitude bounds: 44° 16.0' N to 44° 55.0' N
"""
# Author: Stuart Pearce
# Created: 2019-04-24

log_format = '%(levelname)s:%(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)


def main(nc_files):
    GH_nc_list = []
    GH_data_days = 0.0
    GH_deployments = 0.0
    GH_15to16_data_days = 0.0
    GH_15to16_deployments = 0.0

    NH_nc_list = []
    NH_data_days = 0.0
    NH_deployments = 0.0
    NH_15to16_data_days = 0.0
    NH_15to16_deployments = 0.0

    # I want to make a persistance dictionary and pickle it, so that if I need
    # adjust the analysis, I can do so without having to do the large expensive
    # I/O reads from the netCDF files.
    data_persist = {}

    GH_lat_bounds = np.array([4645.000, 4715.500])  # lower, upper
    NH_lat_bounds = np.array([4416.000, 4455.000])  # lower, upper

    # convert the ISO latitudes to decimal degrees
    GH_lat_bounds = iso2deg(GH_lat_bounds)
    NH_lat_bounds = iso2deg(NH_lat_bounds)
    
    
    for nc_file in nc_files:
        deployment = os.path.basename(nc_file).replace('.dbd.nc', '')
        logging.info("Running deployment {:s}".format(deployment))
        # open deployment flight data and get timestamps and latitude data
        fltdata = netCDF4.Dataset(nc_file)
        timestamps = fltdata.variables['m_present_time'][:]
        start_year = dt.datetime.utcfromtimestamp(timestamps[0]).year
        end_year = dt.datetime.utcfromtimestamp(timestamps[-1]).year
        if end_year < 2015:
            continue
        lats = fltdata.variables['m_gps_lat'][:]
        fltdata.close()
        del fltdata

        # convert gps lats to decimal degrees
        lats = iso2deg(lats)
        len_deployment = (timestamps[-1] - timestamps[0])/86400  # in days
        # len_deployment does not include drift time after malfunction
        
        # open deployment science data and get timestamps and chlorophyll data
        sci_nc_file = nc_file.replace('.dbd.', '.ebd.')
        scidata = netCDF4.Dataset(sci_nc_file)
        sci_ts = scidata.variables['sci_m_present_time'][:]
        chlor_data = scidata.variables['sci_flbbcd_chlor_units'][:]
        scidata.close()
        del scidata
       
        # get the timestamps of chlorophyll data
        data_times = sci_ts[np.isfinite(chlor_data)]
        
        # get lat values of the chlorophyll data
        latsii = np.isfinite(lats)
        sci_lats = np.interp(data_times, timestamps[latsii], lats[latsii])
        
        data_persist[deployment] = np.array([data_times, sci_lats])
        
        # find times where chlorophyll positions fall within the GH line lat bounds
        GH_times = data_times[
            np.logical_and(
                sci_lats > GH_lat_bounds[0], 
                sci_lats < GH_lat_bounds[1])]
                        
        # if any chlorophyll data on the GH line, sum the number of data days
        #   This code omits data gaps larger than 24 hours from the summation
        #   See the get_data_duration function below.
        if len(GH_times) > 1:
            logging.info("Deployment has GH data")
            GH_sampling_days = get_data_duration(GH_times)/86400.
            logging.info("GH sampling number of days {:.2f}".format(GH_sampling_days))
            GH_data_days += GH_sampling_days
            GH_nc_list.append(deployment)
            
            percent_deploy_on_GH = np.round(GH_sampling_days / len_deployment, 3)
            logging.info("GH percent of deployment {:.2f}".format(percent_deploy_on_GH))
            GH_deployments += percent_deploy_on_GH
            if start_year >= 2015 and end_year <= 2016:
                GH_15to16_data_days += GH_sampling_days
                GH_15to16_deployments += percent_deploy_on_GH
            
            
        # find where chlorophyll data lats fall within the NH line lat bounds
        NH_times = data_times[
            np.logical_and(
                sci_lats > NH_lat_bounds[0], 
                sci_lats < NH_lat_bounds[1])]
                
        # if any chlorophyll data on the NH line, record the number of days of data
        if len(NH_times) > 1:
            logging.info("Deployment has NH data")
            NH_sampling_days = get_data_duration(NH_times)/86400.
            logging.info("NH sampling number of days {:.2f}".format(NH_sampling_days))
            NH_data_days += NH_sampling_days
            NH_nc_list.append(deployment)
            
            percent_deploy_on_NH = np.round(NH_sampling_days / len_deployment, 3)
            logging.info("NH percent of deployment {:.2f}".format(percent_deploy_on_NH))
            NH_deployments += percent_deploy_on_NH
            if start_year >= 2015 and end_year <= 2016:
                NH_15to16_data_days += NH_sampling_days
                NH_15to16_deployments += percent_deploy_on_NH
    logging.info("Finished loop and writing results")
    with open('days_of_gldata_results.csv', 'w') as fid:
        fid.write(
            "2015-2016 Deployments,2015-2016 Days of Data,"
            "2015-2019 Deployments,2015-2019 Days of Data\n")
        fid.write(
            "Gray's Harbor WA,{:.0f},{:.2f},{:.0f},{:.2f}\n".format(
                GH_15to16_deployments, GH_15to16_data_days,
                GH_deployments, GH_data_days)
        )
        fid.write(
            "Newport OR,{:.0f},{:.2f},{:.0f},{:.2f}\n".format(
                NH_15to16_deployments, NH_15to16_data_days,
                NH_deployments, NH_data_days)
        )
    logging.info("writing pickle")
    with open('data_days_results.pkl', 'wb') as pkl:
        pickle.dump(data_persist, pkl)

def get_data_duration(times):
    dt = np.diff(times)
    gaps = np.flatnonzero(dt > 86400.0)
    gaps = np.append(gaps, len(times)-1)  # appends the end time index
    tstart_section = times[0]
    data_duration = 0
    for gap in gaps:
        tend_section = times[gap]
        data_duration += tend_section - tstart_section
        if gap+1 < len(times):
            tstart_section = times[gap+1] 
    return data_duration

if __name__ == "__main__":
    logging.info(sys.version)
    logging.info('starting the run')
    #logging.info("sys.argv = {:s}".format(repr(sys.argv[1:])))
    nc_files = sys.argv[1:]
    main(nc_files)
