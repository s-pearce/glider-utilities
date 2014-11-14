#!/usr/bin/env python

"""
@package glider_utils
@file glider_utils.py
@author Stuart Pearce & Chris Wingard
@brief Module containing glider utiliities
"""
__author__ = 'Stuart Pearce & Chris Wingard'
__license__ = 'Apache 2.0'
import numpy as np
import warnings
#import pdb
import re
#import pygsw.vectors as gsw

class DbaDataParser(object):
    """
    A class that parses a glider data file and holds it in dictionaries.

    GliderParsedData parses a Slocum Electric Glider data file that has
    been converted to ASCII from binary, and holds the self describing
    header data in a header dictionary and the data in a data dictionary
    using the column labels as the dictionary keys.

    Construct an instance of GliderParsedData using the filename of the
    ASCII file containing the glider data.
    E.g.:
        glider_data = GliderParsedData('glider_data_file.mbd')

    glider_data.hdr_dict holds the header dictionary with the self
    describing ASCII tags from the file as keys.
    data_dict holds a data dictionary with the variable names (column
    labels) as keys.
    A sub-dictionary holds the name of the variable (same as the key),
    the data units, the number of binary bytes used to store each
    variable type, the name of the variable, and the data using the
    keys:
    'Name'
    'Units'
    'Number_of_Bytes'
    'Data'

    For example, to retrieve the data for 'variable_name':
        vn_data = glider_data.data_dict['variable_name]['Data']
    """

    def __init__(self, filename):
        self._fid = open(filename, 'r')
        self.hdr_dict = {}
        self.data_dict = {}
        self._read_header()
        self._read_data()
        self._fid.close()

    def _read_header(self):
        """
        Read in the self describing header lines of an ASCII glider data
        file.
        """
        # There are usually 14 header lines, start with 14,
        # and check the 'num_ascii_tags' line.
        num_hdr_lines = 14
        header_pattern = r'(.*): (.*)$'
        header_re = re.compile(header_pattern)
        #pdb.set_trace()
        hdr_line = 1
        while hdr_line <= num_hdr_lines:
            line = self._fid.readline()
            match = header_re.match(line)
            if match:
                key = match.group(1)
                value = match.group(2)
                value = value.strip()
                if 'num_ascii_tags' in key:
                    num_hdr_lines = int(value)
                self.hdr_dict[key] = value
            hdr_line += 1

    def _read_data(self):
        """
        Read in the column labels, data type, number of bytes of each
        data type, and the data from an ASCII glider data file.
        """
        column_labels = self._fid.readline().split()
        column_type = self._fid.readline().split()
        column_num_bytes = self._fid.readline().split()

        # read each row of data & use np.array's ability to grab a
        # column of an array
        data = []
        #pdb.set_trace()
        for line in self._fid.readlines():
            data.append(line.split())
        data_array = np.array(data, dtype=np.float)  # NOTE: this is an array of strings

        # warn if # of described data rows != to amount read in.
        num_columns = int(self.hdr_dict['sensors_per_cycle'])
        if num_columns != data_array.shape[1]:
            warnings.warn('Glider data file does not have the same' +
                          'number of columns as described in header.\n' +
                          'described %d, actual %d' % (num_columns,
                                                       data_array.shape[1])
                          )

        # extract data to dictionary
        for ii in range(num_columns):
            units = column_type[ii]
            data_col = data_array[:, ii]

            self.data_dict[column_labels[ii]] = {
                'Name': column_labels[ii],
                'Units': units,
                'Number_of_Bytes': int(column_num_bytes[ii]),
                'Data': data_col
            }

            # change ISO lat or lon format to decimal degrees
            if units == 'lat' or units == 'lon':
                min_d100, deg = np.modf(data_col/100.)
                deg_col = deg + (min_d100*100.)/60.
                self.data_dict[column_lables[ii]]['Data_deg'] = deg_col

        self.data_keys = column_labels


class DataVizDataParser(DbaDataParser):
    """
    A class that parses a glider data file and holds it in dictionaries.

    GliderParsedData parses a Slocum Electric Glider data file that has
    been converted to ASCII from binary, and holds the self describing
    header data in a header dictionary and the data in a data dictionary
    using the column labels as the dictionary keys.

    Construct an instance of GliderParsedData using the filename of the
    ASCII file containing the glider data.
    E.g.:
        glider_data = GliderParsedData('glider_data_file.mbd')

    glider_data.hdr_dict holds the header dictionary with the self
    describing ASCII tags from the file as keys.
    data_dict holds a data dictionary with the variable names (column
    labels) as keys.
    A sub-dictionary holds the name of the variable (same as the key),
    the data units, the number of binary bytes used to store each
    variable type, the name of the variable, and the data using the
    keys:
    'Name'
    'Units'
    'Number_of_Bytes'
    'Data'

    For example, to retrieve the data for 'variable_name':
        vn_data = glider_data.data_dict['variable_name]['Data']
    """

    def _read_header(self):
        pass
    
    def _read_data(self):
        """
        Read in the column labels, data type/units, and the data from an Data Visualizer data file.
        """
        filename_hdr = self._fid.readline()
        column_labels = self._fid.readline().split()
        column_type = self._fid.readline().split()
        #column_num_bytes = self._fid.readline().split()

        # read each row of data & use np.array's ability to grab a
        # column of an array
        data = []
        for line in self._fid.readlines():
            data.append(line.split())
        data_array = np.array(data)  # NOTE: can't make floats because of lat & lon

        num_columns = len(column_labels)

        # extract data to dictionary
        for ii in range(num_columns):
            self.data_dict[column_labels[ii]] = {
                'Name': column_labels[ii],
                'Units': column_type[ii],
                #'Number_of_Bytes': int(column_num_bytes[ii]),
                'Data': data_array[:, ii]
            }
        self.data_keys = column_labels

        
class GliderData(dict):
    """ An object specifically to store Slocum glider data.
    """
    def __init__():
        dict.__init__

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
        print 'lat: %.4f, lon: %.4f' % (lat,lon)
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
        print 'lat: %s, lon: %s' % (iso_lat_str, iso_lon_str)
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
        print 'lat: %.4f, lon: %.4f' % (lat,lon)
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
        print 'lat: %s, lon: %s' % (iso_lat_str, iso_lon_str)
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
        print "lat: %s %s' %s\", lon: %s %s' %s\"" % (lat_deg, lat_min, lat_sec, lon_min, lon_sec


# class A(np.ndarray):

    # def __new__(cls,data,units):
        # obj = np.asarray(data).view(cls)
        # obj.units = units
        
        # return obj

    # def __array_finalize(self,obj):
        # if obj is None: return


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