#! /usr/bin/python
"""gliderstate_parser.py
Author: Stuart Pearce 2017-01-27
Used by: gliders_kml.py in /var/www/cgi-bin/ (and gliders_kml_OOC.py)
"""
import xml.etree.ElementTree as ET
import re
import datetime as dt
import numpy as np

from ..geo import iso2deg

## Definitions ##
# def iso2deg(pos):
    # """iso2deg converts a glider iso position element to 
    # a decimal degree position element.
    # E.G. 
    # > lat = 4434.456  # a latitude, 44 deg 34.456 min
    # > iso2deg(lat)
    # 44.574
    # """
    # minutes, deg = np.modf(pos/100.)
    # minutes *= 100.
    # decimal_frac = minutes/60.
    # pos_deg = deg + decimal_frac
    # return pos_deg

class GSxml(object):
    """ A gliderState.xml object that parses and stores the positions and waypoint 
    information from a gliderState.xml state file.
    
    Positions are in both iso format (DDDMM.MMM) and degree format (DDD.DDD) under
    the attributes .lats.iso & .lons.iso and .lats.deg & .lons.deg as lists.
    A list of timestamps for each position is the .timestamps attribute in datetime objects.
    The waypoints are stored in numbered dictionaries in both iso and degree format under
    the .waypts.iso and .waypts.deg attributes.
    """

    def __init__(self, gsxmlfile):
        """ to initialize object provide a filename string or file object of the 
        gliderstate.xml file.
        """
        self.timestamps = []
        self.kml_timestamps = []
        self.lons_iso = []
        self.lons_deg = []
        self.lats_iso = []
        self.lats_deg = []
        self.waypts_iso = []
        self.waypts_deg = []
        self.next_waypt = None
        self.next_waypt_dist = None
        self.next_waypt_brng = None
        self.parse_GSxml(gsxmlfile)


    def parse_GSxml(self, gsxmlfile):
        """parses out the gliderState.xml file using the xml etree package
        """
        tree =  ET.parse(gsxmlfile)
        root = tree.getroot()
        self._get_waypts(root)
        self._get_positions(root)
        self._get_next_waypt_info(root)


    def _get_waypts(self, root):
        """pulls the glider's current waypoint set out of the gliderState.xml file
        """
        waypts = root.findall('./writeRouteAssignment/route/waypoints/Waypoint')
        for waypt in waypts:
            waypt_name = waypt.find('name').text
            waypt_lat = float(waypt.find('latitude').text)
            waypt_lon = float(waypt.find('longitude').text)
            self.waypts_iso.append((waypt_name, waypt_lon, waypt_lat))
            self.waypts_deg.append((waypt_name, iso2deg(waypt_lon), iso2deg(waypt_lat)))


    def _get_positions(self, root):
        """pulls the gliders surface position history out of the gliderState.xml file.
        """
        # A timestamp regex to parse gliderState.xml's timestamp
        ts_regex = re.compile(
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\+|-)(\d{2})(\d{2})')
        for report in root.findall('./writeTrack/report'):  # positions are recorded in "report" elements
            # timestamps
            time_ = report.find('time').text
            match = ts_regex.match(time_)
            if match:
                ts = match.group(1)  # timestamp
                tz_sn = match.group(2)  # timezone sign 
                tz_hr = match.group(3)  # timezone hour
                tz_mn = match.group(4)  # timezone minute
            dt_ts = dt.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
            self.timestamps.append(dt_ts)
            
            # latitudes and longitudes
            lat = float(report.find('location/lat').text)
            lon = float(report.find('location/lon').text)
            self.lats_iso.append(lat)
            self.lons_iso.append(lon)
            self.lats_deg.append(iso2deg(lat))
            self.lons_deg.append(iso2deg(lon))
    
    
    def _get_next_waypt_info(self, root):
        next_waypt_regex = re.compile(r'\((-*\d{4}\.\d+),(-*\d{5}\.\d+)\)')
        bearing_regex = re.compile(r'(\d+)deg')
        for dataParam in root.findall('./writeTrack/dataParameters/dataParameter'):
            name = dataParam.find('name')
            value = dataParam.find('value')
            if name.text == 'Next waypoint coordinates':
                match = next_waypt_regex.match(value.text)
                if match:
                    lat = iso2deg(float(match.group(1)))
                    lon = iso2deg(float(match.group(2)))
                    self.next_waypt = (lon, lat)
            if name.text == 'Next waypoint range':
                self.next_waypt_dist = value.text
            if name.text == 'Next waypoint bearing':
                match = bearing_regex.match(value.text)
                if match:
                    self.next_waypt_brng = int(match.group(1))