#!/usr/bin/env python

"""
@package glider_utils
@file conv.py
@author Stuart Pearce & Chris Wingard
@brief Module containing common conversions for glider utiliities
"""
__author__ = 'Stuart Pearce & Chris Wingard'
__license__ = 'Apache 2.0'
import numpy as np
import warnings
#import pdb
import re
#import pygsw.vectors as gsw


def convert_lat_lon(latlon_str, printIt=0):
    latlons = latlon_str.split()
    lat_ = latlons[0]
    lon_ = latlons[2]

    lat_deg = float(lat_[0:2])
    lat_min = float(lat_[2:])
    lat = lat_deg + lat_min/60.

    lon_deg = float(lon_[0:4])
    lon_min = float(lon_[4:])
    lon = lon_deg - lon_min/60.

    if printIt:
        print('lat: %.4f, lon: %.4f' % (lat,lon))
    else:
        return lat, lon

def r_convert_lat_lon(lat, lon, printIt=0):
    lat_frac, lat_deg = np.modf(lat)
    lon_frac, lon_deg = np.modf(lon)
    lat_min = lat_frac * 60.
    lon_min = lon_frac * 60.
    iso_lat_str = "%d%06.3f" % (lat_deg, abs(lat_min))
    iso_lon_str = "%d%06.3f" % (lon_deg, abs(lon_min))
    if printIt:
        print('lat: %s, lon: %s' % (iso_lat_str, iso_lon_str))
    else:
        return iso_lat_str, iso_lon_str
    
def iso2deg(latlon_str, printIt=0):
    latlons = latlon_str.split()
    lat_ = latlons[0]
    lon_ = latlons[2]

    lat_deg = float(lat_[0:2])
    lat_min = float(lat_[2:])
    lat = lat_deg + lat_min/60.

    lon_deg = float(lon_[0:4])
    lon_min = float(lon_[4:])
    lon = lon_deg - lon_min/60.

    if printIt:
        print('lat: %.4f, lon: %.4f' % (lat,lon))
    else:
        return lat, lon

def deg2iso(lat, lon, printIt=0):
    lat_frac, lat_deg = np.modf(lat)
    lon_frac, lon_deg = np.modf(lon)
    lat_min = lat_frac * 60.
    lon_min = lon_frac * 60.
    iso_lat_str = "%d%06.3f" % (lat_deg, abs(lat_min))
    iso_lon_str = "%d%06.3f" % (lon_deg, abs(lon_min))
    if printIt:
        print('lat: %s, lon: %s' % (iso_lat_str, iso_lon_str))
    else:
        return iso_lat_str, iso_lon_str

def deg2dms(lat,lon, printIt=0):
    lat_frac, lat_deg = np.modf(lat)
    lon_frac, lon_deg = np.modf(lon)
    lat_min = lat_frac * 60
    lon_min = lon_frac * 60
    lon_sfrac, lon_min = np.modf(lon_min)
    lat_sfrac, lat_min = np.modf(lat_min)
    lat_sec = lat_sfrac * 60
    lon_sec = lon_sfrac * 60
    if printIt:
        print("lat: %s %s' %s\", lon: %s %s' %s\"" % (lat_deg, lat_min, lat_sec, lon_min, lon_sec))
