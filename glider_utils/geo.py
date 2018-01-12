#!/usr/bin/env python

"""
@package glider_utils
@file conv.py
@author Stuart Pearce & Chris Wingard
@brief Module containing common geographic glider utiliities
"""
__author__ = 'Stuart Pearce & Chris Wingard'
__license__ = 'Apache 2.0'
import numpy as np
import warnings
#import pdb
import re
#import pygsw.vectors as gsw


def isostr2deg(latlon_str, printIt=0):
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

def iso2deg(iso_pos_element):
    minutes, degrees = np.modf(iso_pos_element / 100.)
    degrees = degrees + (minutes*100./60.)
    return degrees

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

def speed2vector(speed, dir, deg=True):
    if deg:
        rad_dir = np.rad2deg(dir)
    else:
        rad_dir = deg
    vx = speed * np.cos(rad_dir)
    vy = speed * np.sin(rad_dir)
    return vx, vy

def vector2speed(vx, vy, deg=True):
    speed = np.sqrt(vx**2 + vy**2)
    dir = np.arctan2(vy, vx)
    if deg:
        dir = np.rad2deg(dir)
    return speed, dir

def azimuth(pt1, pt2):
    lat1 = np.rad2deg(pt1[0])
    lon1 = np.rad2deg(pt1[1])
    lat2 = np.rad2deg(pt2[0])
    lon2 = np.rad2deg(pt2[1])
    f = 1/298.257223563  # squish for WGS84 ellipsoid
    e2 = f * (2-f)
    lam = (1-e2) * (np.tan(lat2)/np.tan(lat1)) + \
        e2 * np.sqrt(
            (1+(1-e2) * np.tan(lat2)**2) / 
            (1+(1-e2) * np.tan(lat1)**2))
    azi = np.arctan(
        np.sin(lon2-lon1) /
        (lam - np.cos(lon2-lon1)) * np.sin(lat1))
    return azi
#
def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371 # km
    phi1 = np.deg2rad(lat1)
    phi2 = np.deg2rad(lat2)
    # lon1 = np.deg2rad(lon1)
    # lon2 = np.deg2rad(lon2)
    del_phi = np.deg2rad(lat2-lat1)
    del_lam = np.deg2rad(lon2-lon1)

    a = (
        np.sin(del_phi/2.)**2. +
        np.cos(phi1) * np.cos(phi2) *
        np.sin(del_lam/2.)**2.
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = R * c
    return d

def bearing(lat1, lon1, lat2, lon2):
    """ Calculate bearing azimuth from two points
    on a sphere.
    
    from http://www.movable-type.co.uk/scripts/latlong.html
    """
    del_lam = np.deg2rad(lon2-lon1)
    phi1 = np.deg2rad(lat1)
    phi2 = np.deg2rad(lat2)
    y = np.sin(del_lam) * np.cos(phi2)
    x = np.cos(phi1) * np.sin(phi2) - np.sin(phi1)*np.cos(phi2)*np.cos(del_lam)
    brng = np.rad2deg(np.arctan2(y, x))
    return brng % 360