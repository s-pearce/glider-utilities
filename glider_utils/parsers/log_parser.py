#!/usr/bin/env python2.7
"""
This is a couple of supporting classes for the glider notification 
system. Particularly this module has the code for parsing out the 
glider's status from a log file. 

-Stuart Pearce, 2015-01-30

"""
import re
import glob
import pdb
import datetime
import numpy as np
import sys


# Regexes 
REASON =  re.compile(
    r'Because:(timeout expired|Hit a waypoint|pitch not commanded|' + 
    'no comms for a while) \[behavior surface_([2-6])')
MISSION =  re.compile(
    r'MissionName:([_A-Z]+\.MI) MissionNum:([-_a-z0-9]+) ' + 
    '\((\d{4}\.\d{4})')
GLIDER =  re.compile(r'Vehicle Name: ([_a-z0-9]+)')
TIMESTAMP = re.compile(
    r'Curr Time: \w+ (\w{3} +\d+ \d{2}:\d{2}:\d{2} 20\d{2}) MT: +(\d+)')
GPS =  re.compile(
    r'GPS Location: +(-*\d+\.*\d*) N (-*\d+\.*\d*) E ' + 
    'measured +([.+e0-9]+) secs ago')
WAYPT_LAT =  re.compile(r'sensor:c_wpt_lat\(lat\)=(-*\d+\.*\d*)')
WAYPT_LON =  re.compile(r'sensor:c_wpt_lon\(lon\)=(-*\d+\.*\d*)')
BATTERY =  re.compile(r'sensor:m_battery\(volts\)=(\d+\.*\d*)')
AMPHRS =  re.compile(r'sensor:m_coulomb_amphr_total\(amp-hrs\)=(\d+\.*\d*)')
DISK_FREE =  re.compile(r'sensor:m_disk_free\(Mbytes\)=(\d+\.*\d*)')
DISK_USED = re.compile(r'sensor:m_disk_usage\(Mbytes\)=(\d+\.*\d*)')
REL_CHARGE = re.compile(
    r'sensor:m_lithium_battery_relative_charge\(%\)=(\d+\.*\d*)')
INFLECTIONS = re.compile(r'sensor:m_tot_num_inflections\(nodim\)=(\d+\.*\d*)')
VACUUM = re.compile(r'sensor:m_vacuum\(inHg\)=(\d+\.*\d*)')
VX = re.compile(r'sensor:m_water_vx\(m/s\)=(-*\d+\.*\d*)')
VY = re.compile(r'sensor:m_water_vy\(m/s\)=(-*\d+\.*\d*)')
CURRENT_CORRECTION = re.compile(
    r' +sensor:u_use_current_correction\(nodim\)=([01])')


# CLASSES
class Position(object):
    """A class for storing a georeferenced position's coordinates with
    conversion methods.
    """
    lat = None
    lon = None
    lat_iso = None
    lon_iso = None
    time = None
    
    def _iso2deg(self, latlon):
        latlon = float(latlon)
        min_d100, deg = np.modf(latlon/100.)
        dec_latlon = deg + (min_d100*100.)/60.
        return dec_latlon

class GliderStatus(object):
    """A class for storing Glider Status info.
    """
    glider = 'NA'
    id = None
    reason = 'NA'
    surface_behavior = 'NA'
    mission = 'NA'
    segment_long = 'NA'
    segment_8x3 = 'NA'
    timestamp = None
    _last_time = None
    ts_mission_secs = None
    gps = Position()
    gps_time = 'NA'
    waypt = Position()
    battery = None
    amphrs = None
    disk_free = 'NA Mbytes'
    disk_used = 'NA Mbytes'
    battery_charge = None
    _last_charge = None
    inflections = None
    vacuum = 'NA inHg'
    water_vx = None
    water_vy = None
    cc = None
    
    def __init__(self, glider_name):
        self.glider = glider_name
        reg = re.search('(\d+)', glider_name)
        if reg:
            self.id = int(reg.group(1))
    

class LogParser(object):
    """A class to parse glider surface log files for information.
    """
    
    def __init__(self, path_to_log, glider_name):
        self.path = path_to_log
        # group 1 = timestamp
        # 2 = GPS latitude
        # 3 = GPS longitude
        # 4 = seconds since GPS was measured
        # 5 = waypoint latititude
        # 6 = waypoint longitude
        # 7 = battery voltage
        # 8 = amphours total
        # 9 = battery relative charge
        # 10 = total inflections
        # 11 = vacuum
        # 12 = east water velocity
        # 13 = north water velocity
        # 14 = current correction
     
        self.regex = {
            'reason': {'pattern': REASON, 'parsed': 0, 'handler': self._reason},
            'mission': {'pattern': MISSION, 'parsed': 0, 'handler': self._mission},
            'glider': {'pattern': GLIDER, 'parsed': 0, 'handler': self._glider},
            'timestamp': {'pattern': TIMESTAMP, 'parsed': 0, 'handler': self._timestamp},
            'GPS': {'pattern': GPS, 'parsed': 0, 'handler': self._gps},
            'waypoint_lat': {'pattern': WAYPT_LAT, 'parsed': 0, 'handler': self._waypt_lat},
            'waypoint_lon': {'pattern': WAYPT_LON, 'parsed': 0, 'handler': self._waypt_lon},
            'battery': {'pattern': BATTERY, 'parsed': 0, 'handler': self._battery},
            'amphrs': {'pattern': AMPHRS, 'parsed': 0, 'handler': self._amphrs},
            'disk_free': {'pattern': DISK_FREE, 'parsed': 0, 'handler': self._disk_free},
            'disk_used': {'pattern': DISK_USED, 'parsed': 0, 'handler': self._disk_used},
            'rel_charge': {'pattern': REL_CHARGE, 'parsed': 0, 'handler': self._rel_charge},
            'inflections': {'pattern': INFLECTIONS, 'parsed': 0, 'handler': self._inflections},
            'vacuum': {'pattern': VACUUM, 'parsed': 0, 'handler': self._vacuum},
            'vx': {'pattern': VX, 'parsed': 0, 'handler': self._vx},
            'vy': {'pattern': VY, 'parsed': 0, 'handler': self._vy},
            'current_correction': {'pattern': CURRENT_CORRECTION, 'parsed': 0, 'handler': self._cc}
        }
        
        self.glider_stat = GliderStatus(glider_name)
    
    def parse_line(self, line):
        """ Receives a line from the readline() function on the log and matches
        it to the correct regex in the self.regex dicitionary.  It then feeds
        the groups from the regex match into the handler for the type of line.
        """
        for key in self.regex.keys():
            if not self.regex[key]['parsed']:
                match = self.regex[key]['pattern'].search(line)
                if match:
                    self.regex[key]['handler'](match.groups())
                    self.regex[key]['parsed'] = 1
                    continue

    def _reason(self, groups):
        """The handler for the regex matched groups for the reason line in a
        glider dockserver log.  Input is a tuple with 2 entries that are
        strings of the reason for surfacing and the behavior stack number.
        """
        self.glider_stat.reason = groups[0]
        self.glider_stat.surface_behavior = groups[1]
        
    def _mission(self, groups):
        """The handler for the regex matched groups for the mission line in a 
        glider dockserver log.  Input is a tuple with 3 entries that is a 
        string of the mission name, and the 2 types of segment names, i.e the
        full name and the 8x3 name.
        """
        self.glider_stat.mission = groups[0]
        self.glider_stat.segment_long = groups[1]
        self.glider_stat.segment_8x3 = groups[2]

    def _glider(self, groups):
        """The handler for the regex matched groups for the vehicle name line 
        in a glider dockserver log.  Input is a tuple with 1 entry that is a 
        string of the glider name.
        """
        if self.glider_stat.glider != groups[0]:
            #log('Incorrect glider info! %s' % groups[0])
            sys.exit()

    def _timestamp(self, groups):
        """The handler for the regex matched groups for the timestamp line in 
        the glider dockserver log.  Input is a tuple with 1 entry that is the
        timestamp string with format as shown below.
        """
        ts = datetime.datetime.strptime(groups[0], '%b %d %H:%M:%S %Y')
        self.glider_stat.timestamp = ts
        self.glider_stat.waypt.time = ts

    def _gps(self, groups):
        """The handler for the regex matched groups for the GPS Position line
        in a glider dockserver log.  Input is a tuple with 3 entries that are
        strings of the latitude and longitude in ISO format (positive Northern
        hemisphere) and the number of seconds elapsed since the GPS position
        was measured which is used to create a timestamp for the GPS
        measurement.
        """
        self.glider_stat.gps.lat_iso = groups[0]
        self.glider_stat.gps.lon_iso = groups[1]
        seconds_offset = datetime.timedelta(seconds = float(groups[2]))
        # we are retrieving this time because it is the closest to the glider
        # surfacing time and is best used to predict the next surface time.
        self.glider_stat.gps.time = self.glider_stat.timestamp - seconds_offset

    def _waypt_lat(self, groups):
        """The handler for the regex matched groups for the c_wpt_lat line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string
        of the latitude in ISO format (positive Northern hemisphere) of the
        glider's current waypoint.
        """
        self.glider_stat.waypt.lat_iso = groups[0]
        self.glider_stat.waypt.lat = self.glider_stat.waypt._iso2deg(groups[0])

    def _waypt_lon(self, groups):
        """The handler for the regex matched groups for the c_wpt_lon line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string
        of the longitude in ISO format (positive Eastern hemisphere) of the
        glider's current waypoint.
        """
        self.glider_stat.waypt.lon_iso = groups[0]
        self.glider_stat.waypt.lon = self.glider_stat.waypt._iso2deg(groups[0])

    def _battery(self, groups):
        """The handler for the regex matched groups for the m_battery line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string
        of the battery voltage in volts.
        """
        self.glider_stat.battery = float(groups[0])
        
    def _amphrs(self, groups):
        """The handler for the regex matched groups for the 
        m_coulomb_amphrs_total line in a glider dockserver log.  Input is a 
        tuple with 1 entry that is a string of the number of amp hours used.
        """
        self.glider_stat.amphrs = float(groups[0])

    def _disk_free(self, groups):
        """The handler for the regex matched groups for the disk_free line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string 
        of the amount of free disk space on the flight compact flash card.
        """
        self.glider_stat.disk_free = float(groups[0])

    def _disk_used(self, groups):
        """The handler for the regex matched groups for the disk_used line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string
        of the amount of disk space used on the flight compact flash card.
        """
        self.glider_stat.disk_used = float(groups[0])

    def _rel_charge(self, groups):
        """The handler for the regex matched groups for the 
        m_lithium_battery_relative_charge line in a glider dockserver log.
        Input is a tuple with 1 entry that is a string of the glider's relative
        battery charge remaining in percentage.
        """
        self.glider_stat.rel_charge = float(groups[0])
        
    def _inflections(self, groups):
        """The handler for the regex matched groups for the 
        m_tot_num_inflections line in a glider dockserver log.  Input is a
        tuple with 1 entry that is a string of the number of total inflections
        that have occurred on that glider (across all deployments).
        """
        self.glider_stat.inflections = int(groups[0])

    def _vacuum(self, groups):
        """The handler for the regex matched groups for the m_vacuum line in a
        glider dockserver log.  Input is a tuple with 1 entry that is a string
        of the measured vacuum inside of the glider in inHg.
        """
        self.glider_stat.vacuum = float(groups[0])

    def _vx(self, groups):
        """The handler for the regex matched groups for the m_water_vx line in
        a glider dockserver log.  Input is a tuple with 1 entry that is a
        string of the estimated average Eastward water velocity in m/s.
        """
        self.glider_stat.vx = float(groups[0])

    def _vy(self, groups):
        """The handler for the regex matched groups for the m_water_vy line in
        a glider dockserver log.  Input is a tuple with 1 entry that is a
        string of the estimated average Northward water velocity in m/s.
        """
        self.glider_stat.vy = float(groups[0])

    def _cc(self, groups):
        """The handler for the regex matched groups for the 
        u_use_current_correction line in a glider dockserver log.  Input is a
        tuple with 1 entry that is a string of the boolean value representing
        whether the current correction function is on or off.
        """
        self.glider_stat.current_correction = int(groups[0])


# timeslist = []
# batterylist = []

# # pdb.set_trace()

    # loglist = glob.glob(self.path + '*.log')
    # loglist.sort()
    # for filename in loglist:
        # # pdb.set_trace()

        # time_ = []
        # battery = []

        # fid = open(filename,'r')
        # with fid:
            # file_str = fid.read()
        # match = 1
        # matches = self.regex.finditer(file_str)
        # for match in matches:
            # if match:
                # time_.append(match.group(1))
                # battery.append(match.group(5))

        # if battery:
            # gliders[glider]['battery'].append(float(battery[-1]))
        # if time_:
            # time_ = time_[-1]
            # #  Oct 23 21:39:50 2014
            # time_ = datetime.datetime.strptime(time_, '%b %d %H:%M:%S %Y')
    
    # battery = gliders[glider]['battery']
    # times = gliders[glider]['times']
    # time_diff = np.array(times[1:]) - np.array(times[:-1])
    # days = np.array(map(datetime.timedelta.total_seconds, time_diff)) / 86400.
    # power_use = (np.array(battery[:-1]) - np.array(battery[1:]))/days



    
