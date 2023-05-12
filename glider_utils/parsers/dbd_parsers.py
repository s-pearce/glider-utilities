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
import os
#import pdb
import re
import logging
#import pygsw.vectors as gsw

DEFAULTBYTES = 500

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
                self.data_dict[column_labels[ii]]['Data_deg'] = deg_col

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



def parse_header(file):
    """Parse the header information in a Slocum glider data file regardless if
    binary or ascii format.
    All header lines of the format 'key: value' are parsed.

    Args:
        file: glider data file to parse
        file_info : boolean flag whether or not to include file information

    Returns:
        A dictionary containing the file metadata
    """
    
    # ToDo:  I could likely improve the speed a lot on this by just starting
    # with the filenames and only searching the bracket of files where the
    # time to look up falls between the Ordianal day of the filename.
    # but then again, it only takes like 8 seconds and will only ever be used
    # by me in single calls to find where a particular event occurs.
    
    # file ends in "bd" indicates a raw Slocum glider binary data file
    bdfile = file.lower().endswith('bd')
    
    # check if the file is binary (works with Python 3 only) to eliminate
    # the case where a file was converted to ascii but not renamed.
    # binaryfile = _determine_if_binary(file)
    # Note: 15% of the runtime is due to this one call.  Since it is really just
    #       me that would EVER use this, we can just change to using the
    #       `endswith("bd")` statement above and cut down on runtime.

    binary = bdfile # and binaryfile
    if binary:
        readingflag = "rb"
    else:
        readingflag = "r"
    
    with open(file, readingflag) as fid:
        header = _parse_header(fid, binary)
    
    return header


def _determine_if_binary(file):
    try:
        with open(file, 'r') as fid:
            line = fid.readline()
        binaryfile = False
    except UnicodeDecodeError:
        binaryfile = True
    return binaryfile


def _readline(fid, binary):
    if binary:
        return fid.readline().decode()
    else:
        return fid.readline()


def _parse_header(fid, binary=False, file_info=True):
    """A Slocum glider data header parser. 
    If binary provide the binary boolean.
    All header lines of the format 'key: value' are parsed.

    Args:
        fid: open glider data file object to parse
        binary: bool
            True if the file is a binary glider data file, False if ascii

    Returns:
        A dictionary containing the file metadata
    """
    
    headers = {}
    try:
        lines_read = 0
        # starting with 14 field/tag lines at the start of the file (the only 
        # value I've ever seen), but will update using `num_ascii_tags`
        n_field_lines = 14
        while lines_read < n_field_lines:
            line = _readline(fid, binary)
            lines_read += 1
            tokens = line.split(': ')
            if len(tokens) != 2:
                break
            kw = tokens[0].strip()
            value = tokens[1].strip()
            headers[kw] = value
            if kw == "num_ascii_tags":
                n_field_lines = int(value)
            
    except IOError as e:
        logging.error('Error parsing {:s} data header: {}'.format(
            fid.name, e))
        return
    except UnicodeDecodeError:
        pass

    if not headers:
        logging.warning('No headers parsed: {:s}'.format(
            fid.name))
        return

    if 'num_ascii_tags' in headers:
        if lines_read != int(headers['num_ascii_tags']):
            logging.warning(
                'Unexpected number of header fields: {:s}'.format(fid.name))
            return
    else:
        logging.warning('num_ascii_tags header line missing: {:s}'.format(
            fid.name))
        return

    # Add source file, and file size
    if file_info:
        headers['source_file'] = os.path.abspath(fid.name)
        # Add the dba file size
        headers['file_size_bytes'] = os.path.getsize(fid.name)

    return headers


def get_fileopen_time(file, bytestoread=DEFAULTBYTES):
    """Get the `fileopen_time` from the header of a glider data file.
    
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `fileopen_time`. Assumes the field
        will be found within these number of bytes.  Default is 500.
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    fileopentime : str
    """
    # this works an order of magnitude faster than _parse_header but requires
    # the assumption that the `fileopen_time` field exists within the first 
    # `bytestoread` bytes
    with open(file, 'rb') as fid:
        hdr_lines = fid.read(bytestoread).decode(errors="ignore")
    match = re.search(
        r'fileopen_time: +(\w{3}_\w{3}_+\d{1,2}_\d{2}:\d{2}:\d{2}_\d{4})\n',
        hdr_lines)
    if match:
        return match.group(1)


def hdr_value(field, file, bytestoread=DEFAULTBYTES):
    """Get a field value from the header of a glider data file.
    
    Parameters
    ----------
    field : str
        Field name
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `field`. Assumes the field value
        will be found within these number of bytes.  Default 500 bytes. 
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    fileopentime : str
    """
    with open(file, 'rb') as fid:
        hdr_lines = fid.read(bytestoread).decode(errors="ignore")
    match = re.search(
        r'{:s}: +(.+)\n'.format(field),
        hdr_lines)
    if match:
        return match.group(1)


def get_cache(file, bytestoread=DEFAULTBYTES):
    """Get cache crc value (cache filename) from the header of a glider data file.
    
    Parameters
    ----------
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `sensor_list_crc`. Assumes the field
        will be found within these number of bytes.  Default is 500.
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    cache_crc : str
    """
    return hdr_value('sensor_list_crc', file, bytestoread=bytestoread)

def get_8x3fn(file, bytestoread=DEFAULTBYTES):
    """Get the 8 digit short filename from the header of a glider data file.
    
    Parameters
    ----------
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `the8x3_filename`. Assumes the field
        will be found within these number of bytes.  Default is 500.
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    fileopentime : str
    """
    return hdr_value('the8x3_filename', file, bytestoread=bytestoread)

def get_fullfn(file, bytestoread=DEFAULTBYTES):
    """Get `full_filename` value from the header of a glider data file.
    
    Parameters
    ----------
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `full_filename`. Assumes the field
        will be found within these number of bytes.  Default is 500.
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    full_filename : str
    """
    return hdr_value('full_filename', file, bytestoread=bytestoread)

def get_mission(file, bytestoread=DEFAULTBYTES):
    """Get a field value from the header of a glider data file.
    
    Parameters
    ----------
    file : str
        Filename of glider data file, binary or ascii
    bytestoread : int
        The number of bytes to read & find `full_filename`. Assumes the field
        will be found within these number of bytes.  Default is 500.
        The entire glider data header is usually around 400 bytes or so.
    
    Returns
    -------
    fileopentime : str
    """
    return hdr_value('mission_name', file, bytestoread=bytestoread)


# Note: shortening the regex does NOT save any time
#def just_get_fileopen_time2(file):
#    """a potentially faster read of fileopen time for finding which file a timestamp
#    occurs in, but requires some assumptions and may not work as well."""
#    with open(file, 'rb') as fid:
#        hdr_lines = fid.read(500).decode(errors="ignore")
#    match = re.search(
#        r'fileopen_time: +(\S+)\n',
#        hdr_lines)
#    if match:
#        return match.group(1)