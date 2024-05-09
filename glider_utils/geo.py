#!/usr/bin/env python

"""
@package glider_utils
@file geo.py
@author Stuart Pearce & Chris Wingard
@brief Module containing common geographic glider utilities
"""
__author__ = 'Stuart Pearce & Chris Wingard'
__license__ = 'Apache 2.0'

import warnings
import re

import numpy as np


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
    """iso2deg converts a glider iso position element to 
    a decimal degree position element.
    E.G. 
    > lat = 4434.456  # a latitude, 44 deg 34.456 min
    > iso2deg(lat)
    44.574
    """
    minutes, degrees = np.modf(iso_pos_element / 100.)
    degrees = degrees + (minutes*100./60.)
    return degrees

def deg2iso(lat, lon):
    """convert decimal degrees position element to degree decimal minutes
    in compact ISO format as a float.
    """
    lat_frac, lat_deg = np.modf(lat)
    lon_frac, lon_deg = np.modf(lon)
    lat_min = lat_frac * 60.
    lon_min = lon_frac * 60.
    lat_iso = np.round(lat_deg * 100 + lat_min, 3)
    lon_iso = np.round(lon_deg * 100 + lon_min, 3)
    return lat_iso, lon_iso

def deg2iso_element(pos_element):
    """convert decimal degrees position element to degree decimal minutes
    in compact ISO format as a float.
    """
    frac, deg = np.modf(pos_element)
    minutes = frac * 60.
    pos_iso = np.round(deg * 100 + minutes, 3)
    return pos_iso

def _deg2iso(lat, lon, printIt=0):
    """older version of deg2iso
    """
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

def deg2iso_pprint(lat, lon):
    """Prints ISO format (degrees, decimal minutes) in a nice format.
    e.g. DD° MM.MMM' N, DDD° MM.MMM' W
    """
    if lat < 0:
        lat_dir = "S"
    else:
        lat_dir = "N"
    
    lat = np.abs(lat)
    lat_deg = int(np.trunc(lat))
    lat_min = (lat - lat_deg) * 60
    
    if lon < 0:
        lon_dir = "W"
    else:
        lon_dir = "E"

    lon = np.abs(lon)
    lon_deg = int(np.trunc(lon))
    lon_min = (lon - lon_deg) * 60
    pos_str = u"{:d}\xb0 {:06.3f}' {}, {:d}\xb0 {:06.3f}' {}".format(
        lat_deg, lat_min, lat_dir, lon_deg, lon_min, lon_dir)
    return pos_str

def deg2dms(lat,lon, printIt=0):
    """ convert decimal degrees to degrees, minutes, seconds format
    """
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
        rad_dir = dir
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
    """Calculate the great circle distance between 2 lat & lon positions
    
    Uses the haversine formula to calculate the great circle distance in
    km between 2 positions.
    Params
    ------
    lat1,lon1 : float (decimal degrees)
        The latitude and longitude of the first position as decimal
        degrees.
    lat2,lon2 : float
        The latitude and longitude of the second position as decimal
        degrees.
    
    returns
    -------
    dist : float (km)
        The great circle distance between positions 1 and 2 in km.
        
    from http://www.movable-type.co.uk/scripts/latlong.html
    """
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


def direction_text(bearing, div=8):
    """Direction text string 
    
    Takes a numerical bearing and returns the text abbreviation 
    for the cardinal directions, N, NE, NNE, etc. according to the
    division `div` argument (defaults to the 8 cardinal directions)
    
    Params
    ------
    bearing : float
        The bearing value to translate into a direction text
    div : Division, optional int value of 4, 8, or 16
        The number of divisions of compass directions to use. Allowed
        divisions are 4, 8, or 16.  8 is the default and is used for any
        number that is not 4, 8, or 16.
        
        4 : N,E,S,W
        8 : N,NE,E,SE,S,SW,W,NW
        16: N,NNE,NE,ENE,E,ESE,SE,SSE,S,SSW,SW,WSW,W,WNW,NW,NNW
    
    Returns
    -------
    direction : str
        The text direction for the bearing input
    
    Borrowed from https://stackoverflow.com/questions/3209899/
    determine-compass-direction-from-one-lat-lon-to-the-other"""

    dirs4 = ["E", "S", "W", "N"]
    dirs8 = ["NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    dirs16 = [
        'NNE', 'NE', 'ENE', 'E',
        'ESE', 'SE', 'SSE', 'S',
        'SSW', 'SW', 'WSW', 'W',
        'WNW', 'NW', 'NNW', 'N']
    
    if div == 4:
        dirs = dirs4
    elif div == 16:
        dirs = dirs16
    else:
        dirs = dirs8

    div_range = (360/div)
    mark = div_range/2
    
    index = (bearing - mark) % 360
    index = int(index / div_range)
    return dirs[index]


def dest_from_dist_and_bearing(lat, lon, bearing, dist):
    """Destination point given distance and bearing from start point
    
    Given a start point, initial bearing, and distance, this will calculate 
    the destination point travelling along a (shortest distance) great 
    circle arc
    
    Params
    ------
    lat,lon : float (decimal degrees)
        The latitude and longitude of the starting position in decimal
        degrees.
    bearing : float (degrees)
        Bearing to follow in degrees from true North
    dist : float (km)
        Distance in kilometers to transit
    
    returns
    -------
    lat2, lon2 : float (decimal degrees)
        The latitude and longitude of the final position in decimal
        degrees.
    
    source: http://www.movable-type.co.uk/scripts/latlong.html
    """
    # Formula:
    # φ2 = asin( sin φ1 * cos δ + cos φ1 * sin δ * cos θ )
    # λ2 = λ1 + atan2( sin θ * sin δ * cos φ1, cos δ − sin φ1 * sin φ2 )
    # where: 
    # φ is latitude, λ is longitude, θ is the bearing (clockwise from north),
    # δ is the angular distance d/R; d being the distance travelled, 
    # and R the earth’s radius
    
    R = 6371  # Radius of earth (km)
    sin = np.sin
    cos = np.cos
    asin = np.arcsin
    atan2 = np.arctan2
    ad = dist / R  # angular distance = distance (km) / Radius of earth (km)
    phi1 = np.radians(lat)
    lam1 = np.radians(lon)
    theta = np.radians(bearing)
    phi2 = asin(sin(phi1) * cos(ad) + cos(phi1) * sin(ad)*cos(theta))
    lam2 = lam1 + atan2(
        sin(theta) * sin(ad) * cos(phi1),
        cos(ad) - sin(phi1) * sin(phi2))
    lat2 = np.degrees(phi2)
    lon2 = np.degrees(lam2)
    # return lat and lon rounded to 6 decimal places
    return np.round(lat2, 6), np.round(lon2, 6)