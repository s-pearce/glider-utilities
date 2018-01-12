"""
@package mi.dataset.parser.adcpa
@file marine-integrations/mi/dataset/parser/adcpa.py
@author Christopher Wingard, using Teledyne ADCP instrument particles developed
    by Roger Unwin.
@brief Dataset code for the Coastal Slocum Glider mounted Teledyne ExplorerDVL
    (ADCPA) particles

Release notes:
    There are small differences between the PD0 formatted data files for the
    Teledyne RDI Workhorse series of ADCPs and the ExplorerDVL. The set of
    particles defined herein, will only work with the ExplorerDVL data files
    downloaded from TWR Coastal Slocum Glider. If the planned for AUVs also use
    the RDI ExplorerDVL, then these particles should apply to that instrument
    as well.

    Note, all binary data produced by the ExplorerDVL (and all other Teledyne
    RDI ADCPs) is little-endian.
"""

import re
from struct import unpack
from calendar import timegm
import datetime as dt
import sys

if sys.version_info.major < 3:
    from exceptions import Exception



###############################################################################
# Data Particles
###############################################################################
# Regex set to find the start of PD0 packet (first 6 bytes of the header data).
# This is more explicit than just the 0x7f7f marker the manual specifies. Using
# this regex helps avoid cases where the marker could actually be in the data
# string, thus giving a false positive data record marker.
DVL_PD0_REGEX = re.compile(
    b'(\x7f\x7f)([\x00-\xFF]{2})(\x00)(\x06|\x07)'
    , re.DOTALL)
class SampleException(Exception):
    CGLDR_ADCPA_PD0_PARSED = 'cgldr_adcpa_pd0_parsed'

class Names(object):
    """
    Constants for the Teledyne RDI ExplorerDVL PD0 formatted data files
    """
    # ION defined timestamp. Not produced by Explorer DVL, but instead derived
    # from the ExplorerDVLs internal clock.
    # INTERNAL_TIMESTAMP = DataParticleKey.INTERNAL_TIMESTAMP

    # Header Data
    HEADER_ID = 'header_id'
    DATA_SOURCE_ID = 'data_source_id'
    NUM_BYTES = 'num_bytes'
    NUM_DATA_TYPES = 'num_data_types'
    OFFSET_DATA_TYPES = 'offset_data_types'

    # Fixed Leader Data
    FIXED_LEADER_ID = 'fixed_leader_id'
    FIRMWARE_VERSION = 'firmware_version'
    FIRMWARE_REVISION = 'firmware_revision'
    SYSCONFIG_FREQUENCY = 'sysconfig_frequency'
    SYSCONFIG_BEAM_PATTERN = 'sysconfig_beam_pattern'
    SYSCONFIG_SENSOR_CONFIG = 'sysconfig_sensor_config'
    SYSCONFIG_HEAD_ATTACHED = 'sysconfig_head_attached'
    SYSCONFIG_VERTICAL_ORIENTATION = 'sysconfig_vertical_orientation'
    DATA_FLAG = 'data_flag'
    LAG_LENGTH = 'lag_length'
    NUM_BEAMS = 'num_beams'
    NUM_CELLS = 'num_cells'
    PINGS_PER_ENSEMBLE = 'pings_per_ensemble'
    DEPTH_CELL_LENGTH = 'depth_cell_length'
    BLANK_AFTER_TRANSMIT = 'blank_after_transmit'
    SIGNAL_PROCESSING_MODE = 'signal_processing_mode'
    LOW_CORR_THRESHOLD = 'low_corr_threshold'
    NUM_CODE_REPETITIONS = 'num_code_repetitions'
    PERCENT_GOOD_MIN = 'percent_good_min'
    ERROR_VEL_THRESHOLD = 'error_vel_threshold'
    TIME_PER_PING_MINUTES = 'time_per_ping_minutes'
    TIME_PER_PING_SECONDS = 'time_per_ping_seconds'
    COORD_TRANSFORM_TYPE = 'coord_transform_type'
    COORD_TRANSFORM_TILTS = 'coord_transform_tilts'
    COORD_TRANSFORM_BEAMS = 'coord_transform_beams'
    COORD_TRANSFORM_MAPPING = 'coord_transform_mapping'
    HEADING_ALIGNMENT = 'heading_alignment'
    HEADING_BIAS = 'heading_bias'
    SENSOR_SOURCE_SPEED = 'sensor_source_speed'
    SENSOR_SOURCE_DEPTH = 'sensor_source_depth'
    SENSOR_SOURCE_HEADING = 'sensor_source_heading'
    SENSOR_SOURCE_PITCH = 'sensor_source_pitch'
    SENSOR_SOURCE_ROLL = 'sensor_source_roll'
    SENSOR_SOURCE_CONDUCTIVITY = 'sensor_source_conductivity'
    SENSOR_SOURCE_TEMPERATURE = 'sensor_source_temperature'
    SENSOR_AVAILABLE_DEPTH = 'sensor_available_depth'
    SENSOR_AVAILABLE_HEADING = 'sensor_available_heading'
    SENSOR_AVAILABLE_PITCH = 'sensor_available_pitch'
    SENSOR_AVAILABLE_ROLL = 'sensor_available_roll'
    SENSOR_AVAILABLE_CONDUCTIVITY = 'sensor_available_conductivity'
    SENSOR_AVAILABLE_TEMPERATURE = 'sensor_available_temperature'
    BIN_1_DISTANCE = 'bin_1_distance'
    TRANSMIT_PULSE_LENGTH = 'transmit_pulse_length'
    REFERENCE_LAYER_START = 'reference_layer_start'
    REFERENCE_LAYER_STOP = 'reference_layer_stop'
    FALSE_TARGET_THRESHOLD = 'false_target_threshold'
    LOW_LATENCY_TRIGGER = 'low_latency_trigger'
    TRANSMIT_LAG_DISTANCE = 'transmit_lag_distance'
    SYSTEM_BANDWIDTH = 'system_bandwidth'
    SERIAL_NUMBER = 'serial_number'

    # Variable Leader Data
    VARIABLE_LEADER_ID = 'variable_leader_id'
    ENSEMBLE_NUMBER = 'ensemble_number'
    ENSEMBLE_NUMBER_INCREMENT = 'ensemble_number_increment'
    REAL_TIME_CLOCK = 'real_time_clock'
    ENSEMBLE_START_TIME = 'ensemble_start_time'
    BIT_RESULT_DEMOD_1 = 'bit_result_demod_1'
    BIT_RESULT_DEMOD_2 = 'bit_result_demod_2'
    BIT_RESULT_TIMING = 'bit_result_timing'
    SPEED_OF_SOUND = 'speed_of_sound'
    TRANSDUCER_DEPTH = 'transducer_depth'
    HEADING = 'heading'
    PITCH = 'pitch'
    ROLL = 'roll'
    SALINITY = 'salinity'
    TEMPERATURE = 'temperature'
    MPT_MINUTES = 'mpt_minutes'
    MPT_SECONDS = 'mpt_seconds'
    HEADING_STDEV = 'heading_stdev'
    PITCH_STDEV = 'pitch_stdev'
    ROLL_STDEV = 'roll_stdev'
    ADC_TRANSMIT_CURRENT = 'adc_transmit_current'
    ADC_TRANSMIT_VOLTAGE = 'adc_transmit_voltage'
    ADC_AMBIENT_TEMP = 'adc_ambient_temp'
    ADC_PRESSURE_PLUS = 'adc_pressure_plus'
    ADC_PRESSURE_MINUS = 'adc_pressure_minus'
    ADC_ATTITUDE_TEMP = 'adc_attitude_temp'
    ADC_ATTITUDE = 'adc_attitude'
    ADC_CONTAMINATION_SENSOR = 'adc_contamination_sensor'
    BUS_ERROR_EXCEPTION = 'bus_error_exception'
    ADDRESS_ERROR_EXCEPTION = 'address_error_exception'
    ILLEGAL_INSTRUCTION_EXCEPTION = 'illegal_instruction_exception'
    ZERO_DIVIDE_INSTRUCTION = 'zero_divide_instruction'
    EMULATOR_EXCEPTION = 'emulator_exception'
    UNASSIGNED_EXCEPTION = 'unassigned_exception'
    WATCHDOG_RESTART_OCCURRED = 'watchdog_restart_occurred'
    BATTERY_SAVER_POWER = 'battery_saver_power'
    PINGING = 'pinging'
    COLD_WAKEUP_OCCURRED = 'cold_wakeup_occurred'
    UNKNOWN_WAKEUP_OCCURRED = 'unknown_wakeup_occurred'
    CLOCK_READ_ERROR = 'clock_read_error'
    UNEXPECTED_ALARM = 'unexpected_alarm'
    CLOCK_JUMP_FORWARD = 'clock_jump_forward'
    CLOCK_JUMP_BACKWARD = 'clock_jump_backward'
    POWER_FAIL = 'power_fail'
    SPURIOUS_DSP_INTERRUPT = 'spurious_dsp_interrupt'
    SPURIOUS_UART_INTERRUPT = 'spurious_uart_interrupt'
    SPURIOUS_CLOCK_INTERRUPT = 'spurious_clock_interrupt'
    LEVEL_7_INTERRUPT = 'level_7_interrupt'
    PRESSURE = 'pressure'
    PRESSURE_VARIANCE = 'pressure_variance'

    # Velocity Data
    VELOCITY_DATA_ID = 'velocity_data_id'
    WATER_VELOCITY_EAST = 'water_velocity_east'
    WATER_VELOCITY_NORTH = 'water_velocity_north'
    WATER_VELOCITY_UP = 'water_velocity_up'
    ERROR_VELOCITY = 'error_velocity'

    # Correlation Magnitude Data
    CORRELATION_MAGNITUDE_ID = 'correlation_magnitude_id'
    CORRELATION_MAGNITUDE_BEAM1 = 'correlation_magnitude_beam1'
    CORRELATION_MAGNITUDE_BEAM2 = 'correlation_magnitude_beam2'
    CORRELATION_MAGNITUDE_BEAM3 = 'correlation_magnitude_beam3'
    CORRELATION_MAGNITUDE_BEAM4 = 'correlation_magnitude_beam4'

    # Echo Intensity Data
    ECHO_INTENSITY_ID = 'echo_intensity_id'
    ECHO_INTENSITY_BEAM1 = 'echo_intensity_beam1'
    ECHO_INTENSITY_BEAM2 = 'echo_intensity_beam2'
    ECHO_INTENSITY_BEAM3 = 'echo_intensity_beam3'
    ECHO_INTENSITY_BEAM4 = 'echo_intensity_beam4'

    # Percent Good Data
    PERCENT_GOOD_ID = 'percent_good_id'
    PERCENT_GOOD_3BEAM = 'percent_good_3beam'
    PERCENT_TRANSFORMS_REJECT = 'percent_transforms_reject'
    PERCENT_BAD_BEAMS = 'percent_bad_beams'
    PERCENT_GOOD_4BEAM = 'percent_good_4beam'

    # Bottom Track Data (only produced if glider is in less than 65 m of water)
    BOTTOM_TRACK_ID = 'bottom_track_id'
    BT_PINGS_PER_ENSEMBLE = 'bt_pings_per_ensemble'
    BT_DELAY_BEFORE_REACQUIRE = 'bt_delay_before_reacquire'
    BT_CORR_MAGNITUDE_MIN = 'bt_corr_magnitude_min'
    BT_EVAL_MAGNITUDE_MIN = 'bt_eval_magnitude_min'
    BT_PERCENT_GOOD_MIN = 'bt_percent_good_min'
    BT_MODE = 'bt_mode'
    BT_ERROR_VELOCITY_MAX = 'bt_error_velocity_max'
    BEAM1_BT_RANGE_LSB = 'beam1_bt_range_lsb'
    BEAM2_BT_RANGE_LSB = 'beam2_bt_range_lsb'
    BEAM3_BT_RANGE_LSB = 'beam3_bt_range_lsb'
    BEAM4_BT_RANGE_LSB = 'beam4_bt_range_lsb'
    EASTWARD_BT_VELOCITY = 'eastward_bt_velocity'
    NORTHWARD_BT_VELOCITY = 'northward_bt_velocity'
    UPWARD_BT_VELOCITY = 'upward_bt_velocity'
    ERROR_BT_VELOCITY = 'error_bt_velocity'
    BEAM1_BT_CORRELATION = 'beam1_bt_correlation'
    BEAM2_BT_CORRELATION = 'beam2_bt_correlation'
    BEAM3_BT_CORRELATION = 'beam3_bt_correlation'
    BEAM4_BT_CORRELATION = 'beam4_bt_correlation'
    BEAM1_EVAL_AMP = 'beam1_eval_amp'
    BEAM2_EVAL_AMP = 'beam2_eval_amp'
    BEAM3_EVAL_AMP = 'beam3_eval_amp'
    BEAM4_EVAL_AMP = 'beam4_eval_amp'
    BEAM1_BT_PERCENT_GOOD = 'beam1_bt_percent_good'
    BEAM2_BT_PERCENT_GOOD = 'beam2_bt_percent_good'
    BEAM3_BT_PERCENT_GOOD = 'beam3_bt_percent_good'
    BEAM4_BT_PERCENT_GOOD = 'beam4_bt_percent_good'
    REF_LAYER_MIN = 'ref_layer_min'
    REF_LAYER_NEAR = 'ref_layer_near'
    REF_LAYER_FAR = 'ref_layer_far'
    BEAM1_REF_LAYER_VELOCITY = 'beam1_ref_layer_velocity'
    BEAM2_REF_LAYER_VELOCITY = 'beam2_ref_layer_velocity'
    BEAM3_REF_LAYER_VELOCITY = 'beam3_ref_layer_velocity'
    BEAM4_REF_LAYER_VELOCITY = 'beam4_ref_layer_velocity'
    BEAM1_REF_CORRELATION = 'beam1_ref_correlation'
    BEAM2_REF_CORRELATION = 'beam2_ref_correlation'
    BEAM3_REF_CORRELATION = 'beam3_ref_correlation'
    BEAM4_REF_CORRELATION = 'beam4_ref_correlation'
    BEAM1_REF_INTENSITY = 'beam1_ref_intensity'
    BEAM2_REF_INTENSITY = 'beam2_ref_intensity'
    BEAM3_REF_INTENSITY = 'beam3_ref_intensity'
    BEAM4_REF_INTENSITY = 'beam4_ref_intensity'
    BEAM1_REF_PERCENT_GOOD = 'beam1_ref_percent_good'
    BEAM2_REF_PERCENT_GOOD = 'beam2_ref_percent_good'
    BEAM3_REF_PERCENT_GOOD = 'beam3_ref_percent_good'
    BEAM4_REF_PERCENT_GOOD = 'beam4_ref_percent_good'
    BT_MAX_DEPTH = 'bt_max_depth'
    BEAM1_RSSI_AMPLITUDE = 'beam1_rssi_amplitude'
    BEAM2_RSSI_AMPLITUDE = 'beam2_rssi_amplitude'
    BEAM3_RSSI_AMPLITUDE = 'beam3_rssi_amplitude'
    BEAM4_RSSI_AMPLITUDE = 'beam4_rssi_amplitude'
    BT_GAIN = 'bt_gain'
    BEAM1_BT_RANGE_MSB = 'beam1_bt_range_msb'
    BEAM2_BT_RANGE_MSB = 'beam2_bt_range_msb'
    BEAM3_BT_RANGE_MSB = 'beam3_bt_range_msb'
    BEAM4_BT_RANGE_MSB = 'beam4_bt_range_msb'

    # Ensemble checksum
    CHECKSUM = 'checksum'

class DVLdata(object):
    """
    """
    def __init__(self):
        """
        """
        # self._data_dict = {}
        for key in Names.__dict__.keys():
            if not(key.startswith('_')):
                self.__dict__[Names.__dict__[key]] = []
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __setitem__(self, key, value):
        self.__dict__[key] = value



class DVLparser(object):
    """Class DVLparser
    A Parser class that extracts the binary data records from a PD0 file format
    produced by a Teledyne RDI Explorer Doppler Velocity Logger (DVL)
    """
    def __init__(self, infile):
        """
        """
        self._dvl = DVLdata()
        with open(infile, 'rb') as f:
            # read in the pd0 data file and find the indexes to the record markers
            data = f.read()
        record_markerpt = [m.start() for m in DVL_PD0_REGEX.finditer(data)]

        # now parse the file, ensemble by ensemble
        for startpt in record_markerpt:
            # particalize the data block received and return the results
            numBytes = unpack("<H", data[startpt+2:startpt+4])[0]
            ensemble = data[startpt:startpt+numBytes+2]

            # sample = FilteringParser._extract_sample(ADCPA_PD0_PARSED_DataParticle,
                                                     # DVL_PD0_REGEX,
                                                     # ensemble)
            self._build_parsed_values(ensemble)

    def return_data(self):
        return self._dvl

    def _build_parsed_values(self, ensemble):
        """
        Parse the beginning portion of the ensemble (Header Data)
        """

        length = unpack("<H", ensemble[2:4])[0]
        data = str(ensemble)

        # Calculate the checksum
        total = int(0)
        for i in range(0, length):
            total += int(ord(data[i]))

        checksum = total & 65535    # bitwise and with 65535 or mod vs 65536

        if checksum != unpack("<H", ensemble[length: length+2])[0]:
            log.debug("Checksum mismatch " + str(checksum) + " != "
                      + str(unpack("<H", ensemble[length: length+2])[0]))
            raise SampleException("Checksum mismatch")

        # save the checksum and process the remainder of the ensemble
        self._dvl[Names.CHECKSUM].append(checksum)

        (header_id, data_source_id, num_bytes, spare, num_data_types) = \
            unpack('<BBHBB', ensemble[0:6])

        self._dvl[Names.HEADER_ID].append(header_id)
        self._dvl[Names.DATA_SOURCE_ID].append(data_source_id)
        self._dvl[Names.NUM_BYTES].append(num_bytes)
        self._dvl[Names.NUM_DATA_TYPES].append(num_data_types)

        offsets = []    # create list for offsets
        strt = 6        # offsets start at byte 6 (using 0 indexing)
        nDT = 1         # counter for n data types
        while nDT <= num_data_types:
            value = unpack('<H', ensemble[strt:strt+2])[0]
            offsets.append(value)
            strt += 2
            nDT += 1

        self._dvl[Names.OFFSET_DATA_TYPES].append(offsets)
        
        bt_not_included = True
        for offset in offsets:
            # for each offset, using the starting byte, determine the data type
            # and then parse accordingly.
            data_type = unpack('<H', ensemble[offset:offset+2])[0]

            # fixed leader data (x00x00)
            if data_type == 0:
                chunk = ensemble[offset:offset+58]
                self.parse_fixed_chunk(chunk)
                iCells = self.num_depth_cells   # grab the # of depth cells
                                                # obtained from the fixed leader
                                                # data type

            # variable leader data (x80x00)
            if data_type == 128:
                chunk = ensemble[offset:offset+60]
                self.parse_variable_chunk(chunk)

            # velocity data (x00x01)
            if data_type == 256:
                # number of bytes is a function of the user selectable number of
                # depth cells (WN command), calculated above
                nBytes = 2 + 8 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self.parse_velocity_chunk(chunk)

            # correlation magnitude data (x00x02)
            if data_type == 512:
                # number of bytes is a function of the user selectable number of
                # depth cells (WN command), calculated above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self.parse_corelation_magnitude_chunk(chunk)

            # echo intensity data (x00x03)
            if data_type == 768:
                # number of bytes is a function of the user selectable number of
                # depth cells (WN command), calculated above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self.parse_echo_intensity_chunk(chunk)

            # percent-good data (x00x04)
            if data_type == 1024:
                # number of bytes is a function of the user selectable number of
                # depth cells (WN command), calculated above
                nBytes = 2 + 4 * iCells
                chunk = ensemble[offset:offset+nBytes]
                self.parse_percent_good_chunk(chunk)

            # bottom track data (x00x06)
            if data_type == 1536:
                chunk = ensemble[offset:offset+81]
                self.parse_bottom_track_chunk(chunk)
                bt_not_included = False

        if bt_not_included:
            self.fill_bt_nans()


    def parse_fixed_chunk(self, chunk):
        """
        Parse the fixed leader portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        (fixed_leader_id, firmware_version, firmware_revision,
         sysconfig_frequency, data_flag, lag_length, num_beams, num_cells,
         pings_per_ensemble, depth_cell_length, blank_after_transmit,
         signal_processing_mode, low_corr_threshold, num_code_repetitions,
         percent_good_min, error_vel_threshold, time_per_ping_minutes,
         time_per_ping_seconds, time_per_ping_hundredths, coord_transform_type,
         heading_alignment, heading_bias, sensor_source, sensor_available,
         bin_1_distance, transmit_pulse_length, reference_layer_start,
         reference_layer_stop, false_target_threshold, SPARE1,
         transmit_lag_distance, SPARE2, system_bandwidth,
         SPARE3, SPARE4, serial_number) = \
            unpack('<HBBHBBBBHHHBBBBHBBBBhhBBHHBBBBHQHBBI', chunk)

        if 0 != fixed_leader_id:
            raise SampleException("fixed_leader_id was not equal to 0")

        # store the number of depth cells for use elsewhere
        self.num_depth_cells = num_cells

        self._dvl[Names.FIXED_LEADER_ID].append(fixed_leader_id)
        self._dvl[Names.FIRMWARE_VERSION].append(firmware_version)
        self._dvl[Names.FIRMWARE_REVISION].append(firmware_revision)

        frequencies = [75, 150, 300, 600, 1200, 2400]

        self._dvl[Names.SYSCONFIG_FREQUENCY].append(frequencies[sysconfig_frequency & 0b00000111])
        self._dvl[Names.SYSCONFIG_BEAM_PATTERN].append(1 if sysconfig_frequency & 0b00001000 else 0)
        self._dvl[Names.SYSCONFIG_SENSOR_CONFIG].append(sysconfig_frequency & 0b00110000 >> 4)
        self._dvl[Names.SYSCONFIG_HEAD_ATTACHED].append(1 if sysconfig_frequency & 0b01000000 else 0)
        self._dvl[Names.SYSCONFIG_VERTICAL_ORIENTATION].append(1 if sysconfig_frequency & 0b10000000 else 0)

        if 0 != data_flag:
            raise SampleException("data_flag was not equal to 0")

        self._dvl[Names.DATA_FLAG].append(data_flag)
        self._dvl[Names.LAG_LENGTH].append(lag_length)
        self._dvl[Names.NUM_BEAMS].append(num_beams)
        self._dvl[Names.NUM_CELLS].append(num_cells)
        self._dvl[Names.PINGS_PER_ENSEMBLE].append(pings_per_ensemble)
        self._dvl[Names.DEPTH_CELL_LENGTH].append(depth_cell_length)
        self._dvl[Names.BLANK_AFTER_TRANSMIT].append(blank_after_transmit)

        if 1 != signal_processing_mode:
            raise SampleException("signal_processing_mode was not equal to 1")

        self._dvl[Names.SIGNAL_PROCESSING_MODE].append(signal_processing_mode)
        self._dvl[Names.LOW_CORR_THRESHOLD].append(low_corr_threshold)
        self._dvl[Names.NUM_CODE_REPETITIONS].append(num_code_repetitions)
        self._dvl[Names.PERCENT_GOOD_MIN].append(percent_good_min)
        self._dvl[Names.ERROR_VEL_THRESHOLD].append(error_vel_threshold)
        self._dvl[Names.TIME_PER_PING_MINUTES].append(time_per_ping_minutes)

        tpp_float_seconds = float(time_per_ping_seconds + (time_per_ping_hundredths/100))
        self._dvl[Names.TIME_PER_PING_SECONDS].append(tpp_float_seconds)
        self._dvl[Names.COORD_TRANSFORM_TYPE].append(coord_transform_type & 0b00011000 >> 3)
        self._dvl[Names.COORD_TRANSFORM_TILTS].append(1 if coord_transform_type & 0b00000100 else 0)
        self._dvl[Names.COORD_TRANSFORM_BEAMS].append(1 if coord_transform_type & 0b0000000 else 0)
        self._dvl[Names.COORD_TRANSFORM_MAPPING].append(1 if coord_transform_type & 0b00000001 else 0)

        # lame, but expedient - mask off un-needed bits
        self.coord_transform_type = (coord_transform_type & 0b00011000) >> 3

        self._dvl[Names.HEADING_ALIGNMENT].append(heading_alignment)
        self._dvl[Names.HEADING_BIAS].append(heading_bias)
        self._dvl[Names.SENSOR_SOURCE_SPEED].append(1 if sensor_source & 0b01000000 else 0)
        self._dvl[Names.SENSOR_SOURCE_DEPTH].append(1 if sensor_source & 0b00100000 else 0)
        self._dvl[Names.SENSOR_SOURCE_HEADING].append(1 if sensor_source & 0b00010000 else 0)
        self._dvl[Names.SENSOR_SOURCE_PITCH].append(1 if sensor_source & 0b00001000 else 0)
        self._dvl[Names.SENSOR_SOURCE_ROLL].append(1 if sensor_source & 0b00000100 else 0)
        self._dvl[Names.SENSOR_SOURCE_CONDUCTIVITY].append(1 if sensor_source & 0b00000010 else 0)
        self._dvl[Names.SENSOR_SOURCE_TEMPERATURE].append(1 if sensor_source & 0b00000001 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_DEPTH].append(1 if sensor_available & 0b00100000 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_HEADING].append(1 if sensor_available & 0b00010000 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_PITCH].append(1 if sensor_available & 0b00001000 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_ROLL].append(1 if sensor_available & 0b00000100 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_CONDUCTIVITY].append(1 if sensor_available & 0b00000010 else 0)
        self._dvl[Names.SENSOR_AVAILABLE_TEMPERATURE].append(1 if sensor_available & 0b00000001 else 0)
        self._dvl[Names.BIN_1_DISTANCE].append(bin_1_distance)
        self._dvl[Names.TRANSMIT_PULSE_LENGTH].append(transmit_pulse_length)
        self._dvl[Names.REFERENCE_LAYER_START].append(reference_layer_start)
        self._dvl[Names.REFERENCE_LAYER_STOP].append(reference_layer_stop)
        self._dvl[Names.FALSE_TARGET_THRESHOLD].append(false_target_threshold)
        self._dvl[Names.TRANSMIT_LAG_DISTANCE].append(transmit_lag_distance)
        self._dvl[Names.SYSTEM_BANDWIDTH].append(system_bandwidth)
        self._dvl[Names.SERIAL_NUMBER].append(serial_number)

    def parse_variable_chunk(self, chunk):
        """
        Parse the variable leader portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        rtc = {}
        (variable_leader_id, ensemble_number, rtc['year'], rtc['month'],
         rtc['day'], rtc['hour'], rtc['minute'], rtc['second'],
         rtc['hundredths'], ensemble_number_increment, error_bit_field,
         reserved_error_bit_field, speed_of_sound, transducer_depth, heading,
         pitch, roll, salinity, temperature, mpt_minutes, mpt_seconds_component,
         mpt_hundredths_component, heading_stdev, pitch_stdev, roll_stdev,
         adc_transmit_current, adc_transmit_voltage, adc_ambient_temp,
         adc_pressure_plus, adc_pressure_minus, adc_attitude_temp,
         adc_attitiude, adc_contamination_sensor, error_status_word_1,
         error_status_word_2, error_status_word_3, error_status_word_4,
         SPARE1, pressure, pressure_variance, SPARE2) = \
            unpack('<HHBBBBBBBBBBHHHhhHhBBBBBBBBBBBBBBBBBBHIII', chunk)

        if 128 != variable_leader_id:
            raise SampleException("variable_leader_id was not equal to 128")

        self._dvl[Names.VARIABLE_LEADER_ID].append(variable_leader_id)
        self._dvl[Names.ENSEMBLE_NUMBER].append(ensemble_number)
        self._dvl[Names.ENSEMBLE_NUMBER_INCREMENT].append(ensemble_number_increment)

        # convert individual date and time values to datetime object and
        # calculate the NTP timestamp (seconds since Jan 1, 1900), per OOI
        # convention
        dts = dt.datetime(2000 + rtc['year'], rtc['month'], rtc['day'],
                          rtc['hour'], rtc['minute'], rtc['second'])
        epts = timegm(dts.timetuple()) + (rtc['hundredths'] / 100.0)  # seconds since 1970-01-01 in UTC
        ntpts = epts + 2208988800

        self._dvl[Names.REAL_TIME_CLOCK].append([rtc['year'], rtc['month'], rtc['day'],
                                                         rtc['hour'], rtc['minute'], rtc['second'], rtc['hundredths']])
        self._dvl[Names.ENSEMBLE_START_TIME].append(epts)
        # self._dvl[Names.INTERNAL_TIMESTAMP].append(epts)

        self._dvl[Names.BIT_RESULT_DEMOD_1].append(1 if error_bit_field & 0b00001000 else 0)
        self._dvl[Names.BIT_RESULT_DEMOD_2].append(1 if error_bit_field & 0b00010000 else 0)
        self._dvl[Names.BIT_RESULT_TIMING].append(1 if error_bit_field & 0b00000010 else 0)
        self._dvl[Names.SPEED_OF_SOUND].append(speed_of_sound)
        self._dvl[Names.TRANSDUCER_DEPTH].append(transducer_depth)
        self._dvl[Names.HEADING].append(heading)
        self._dvl[Names.PITCH].append(pitch)
        self._dvl[Names.ROLL].append(roll)
        self._dvl[Names.SALINITY].append(salinity)
        self._dvl[Names.TEMPERATURE].append(temperature)
        self._dvl[Names.MPT_MINUTES].append(mpt_minutes)

        mpt_seconds = float(mpt_seconds_component + (mpt_hundredths_component/100))
        self._dvl[Names.MPT_SECONDS].append(mpt_seconds)
        self._dvl[Names.HEADING_STDEV].append(heading_stdev)
        self._dvl[Names.PITCH_STDEV].append(pitch_stdev)
        self._dvl[Names.ROLL_STDEV].append(roll_stdev)
        self._dvl[Names.ADC_TRANSMIT_CURRENT].append(adc_transmit_current)
        self._dvl[Names.ADC_TRANSMIT_VOLTAGE].append(adc_transmit_voltage)
        self._dvl[Names.ADC_AMBIENT_TEMP].append(adc_ambient_temp)
        self._dvl[Names.ADC_PRESSURE_PLUS].append(adc_pressure_plus)
        self._dvl[Names.ADC_PRESSURE_MINUS].append(adc_pressure_minus)
        self._dvl[Names.ADC_ATTITUDE_TEMP].append(adc_attitude_temp)
        self._dvl[Names.ADC_ATTITUDE].append(adc_attitiude)
        self._dvl[Names.ADC_CONTAMINATION_SENSOR].append(adc_contamination_sensor)
        self._dvl[Names.BUS_ERROR_EXCEPTION].append(1 if error_status_word_1 & 0b00000001 else 0)
        self._dvl[Names.ADDRESS_ERROR_EXCEPTION].append(1 if error_status_word_1 & 0b00000010 else 0)
        self._dvl[Names.ILLEGAL_INSTRUCTION_EXCEPTION].append(1 if error_status_word_1 & 0b00000100 else 0)
        self._dvl[Names.ZERO_DIVIDE_INSTRUCTION].append(1 if error_status_word_1 & 0b00001000 else 0)
        self._dvl[Names.EMULATOR_EXCEPTION].append(1 if error_status_word_1 & 0b00010000 else 0)
        self._dvl[Names.UNASSIGNED_EXCEPTION].append(1 if error_status_word_1 & 0b00100000 else 0)
        self._dvl[Names.WATCHDOG_RESTART_OCCURRED].append(1 if error_status_word_1 & 0b01000000 else 0)
        self._dvl[Names.BATTERY_SAVER_POWER].append(1 if error_status_word_1 & 0b10000000 else 0)
        self._dvl[Names.PINGING].append(1 if error_status_word_1 & 0b00000001 else 0)
        self._dvl[Names.COLD_WAKEUP_OCCURRED].append(1 if error_status_word_1 & 0b01000000 else 0)
        self._dvl[Names.UNKNOWN_WAKEUP_OCCURRED].append(1 if error_status_word_1 & 0b10000000 else 0)
        self._dvl[Names.CLOCK_READ_ERROR].append(1 if error_status_word_3 & 0b00000001 else 0)
        self._dvl[Names.UNEXPECTED_ALARM].append(1 if error_status_word_3 & 0b00000010 else 0)
        self._dvl[Names.CLOCK_JUMP_FORWARD].append(1 if error_status_word_3 & 0b00000100 else 0)
        self._dvl[Names.CLOCK_JUMP_BACKWARD].append(1 if error_status_word_3 & 0b00001000 else 0)
        self._dvl[Names.POWER_FAIL].append(1 if error_status_word_4 & 0b00001000 else 0)
        self._dvl[Names.SPURIOUS_DSP_INTERRUPT].append(1 if error_status_word_4 & 0b00010000 else 0)
        self._dvl[Names.SPURIOUS_UART_INTERRUPT].append(1 if error_status_word_4 & 0b00100000 else 0)
        self._dvl[Names.SPURIOUS_CLOCK_INTERRUPT].append(1 if error_status_word_4 & 0b01000000 else 0)
        self._dvl[Names.LEVEL_7_INTERRUPT].append(1 if error_status_word_4 & 0b10000000 else 0)
        self._dvl[Names.PRESSURE].append(pressure)
        self._dvl[Names.PRESSURE_VARIANCE].append(pressure_variance)

    def parse_velocity_chunk(self, chunk):
        """
        Parse the velocity portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 2 / 4
        offset = 0

        velocity_data_id = unpack("<H", chunk[0:2])[0]
        if 256 != velocity_data_id:
            raise SampleException("velocity_data_id was not equal to 256")

        self._dvl[Names.VELOCITY_DATA_ID].append(velocity_data_id)

        water_velocity_east = []
        water_velocity_north = []
        water_velocity_up = []
        error_velocity = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<hhhh', chunk[offset + 2: offset + 10])
            water_velocity_east.append(a)
            water_velocity_north.append(b)
            water_velocity_up.append(c)
            error_velocity.append(d)
            offset += 4 * 2
        self._dvl[Names.WATER_VELOCITY_EAST].append(water_velocity_east)
        self._dvl[Names.WATER_VELOCITY_NORTH].append(water_velocity_north)
        self._dvl[Names.WATER_VELOCITY_UP].append(water_velocity_up)
        self._dvl[Names.ERROR_VELOCITY].append(error_velocity)

    def parse_corelation_magnitude_chunk(self, chunk):
        """
        Parse the corelation magnitude portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        correlation_magnitude_id = unpack("<H", chunk[0:2])[0]
        if 512 != correlation_magnitude_id:
            raise SampleException("correlation_magnitude_id was not equal to 512")

        self._dvl[Names.CORRELATION_MAGNITUDE_ID].append(correlation_magnitude_id)

        correlation_magnitude_beam1 = []
        correlation_magnitude_beam2 = []
        correlation_magnitude_beam3 = []
        correlation_magnitude_beam4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<BBBB', chunk[offset + 2: offset + 6])
            correlation_magnitude_beam1.append(a)
            correlation_magnitude_beam2.append(b)
            correlation_magnitude_beam3.append(c)
            correlation_magnitude_beam4.append(d)
            offset += 4

        self._dvl[Names.CORRELATION_MAGNITUDE_BEAM1].append(correlation_magnitude_beam1)
        self._dvl[Names.CORRELATION_MAGNITUDE_BEAM2].append(correlation_magnitude_beam2)
        self._dvl[Names.CORRELATION_MAGNITUDE_BEAM3].append(correlation_magnitude_beam3)
        self._dvl[Names.CORRELATION_MAGNITUDE_BEAM4].append(correlation_magnitude_beam4)

    def parse_echo_intensity_chunk(self, chunk):
        """
        Parse the echo intensity portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        echo_intensity_id = unpack("<H", chunk[0:2])[0]
        if 768 != echo_intensity_id:
            raise SampleException("echo_intensity_id was not equal to 768")
        self._dvl[Names.ECHO_INTENSITY_ID].append(echo_intensity_id)

        echo_intesity_beam1 = []
        echo_intesity_beam2 = []
        echo_intesity_beam3 = []
        echo_intesity_beam4 = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<BBBB', chunk[offset + 2: offset + 6])
            echo_intesity_beam1.append(a)
            echo_intesity_beam2.append(b)
            echo_intesity_beam3.append(c)
            echo_intesity_beam4.append(d)
            offset += 4

        self._dvl[Names.ECHO_INTENSITY_BEAM1].append(echo_intesity_beam1)
        self._dvl[Names.ECHO_INTENSITY_BEAM2].append(echo_intesity_beam2)
        self._dvl[Names.ECHO_INTENSITY_BEAM3].append(echo_intesity_beam3)
        self._dvl[Names.ECHO_INTENSITY_BEAM4].append(echo_intesity_beam4)

    def parse_percent_good_chunk(self, chunk):
        """
        Parse the percent good portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        N = (len(chunk) - 2) / 4
        offset = 0

        percent_good_id = unpack("<H", chunk[0:2])[0]
        if 1024 != percent_good_id:
            raise SampleException("percent_good_id was not equal to 1024")

        self._dvl[Names.PERCENT_GOOD_ID].append(percent_good_id)

        percent_good_3beam = []
        percent_transforms_reject = []
        percent_bad_beams = []
        percent_good_4beam = []
        for row in range(1, N):
            (a, b, c, d) = unpack('<BBBB', chunk[offset + 2: offset + 6])
            percent_good_3beam.append(a)
            percent_transforms_reject.append(b)
            percent_bad_beams.append(c)
            percent_good_4beam.append(d)
            offset += 4
        self._dvl[Names.PERCENT_GOOD_3BEAM].append(percent_good_3beam)
        self._dvl[Names.PERCENT_TRANSFORMS_REJECT].append(percent_transforms_reject)
        self._dvl[Names.PERCENT_BAD_BEAMS].append(percent_bad_beams)
        self._dvl[Names.PERCENT_GOOD_4BEAM].append(percent_good_4beam)

    def parse_bottom_track_chunk(self, chunk):
        """
        Parse the bottom track portion of the particle

        @throws SampleException If there is a problem with sample creation
        """
        (bottom_track_id, bt_pings_per_ensemble, bt_delay_before_reacquire,
         bt_corr_magnitude_min, bt_eval_magnitude_min, bt_percent_good_min,
         bt_mode, bt_error_velocity_max, RESERVED, beam1_bt_range_lsb, beam2_bt_range_lsb,
         beam3_bt_range_lsb, beam4_bt_range_lsb, eastward_bt_velocity,
         northward_bt_velocity, upward_bt_velocity, error_bt_velocity,
         beam1_bt_correlation, beam2_bt_correlation, beam3_bt_correlation,
         beam4_bt_correlation, beam1_eval_amp, beam2_eval_amp, beam3_eval_amp,
         beam4_eval_amp, beam1_bt_percent_good, beam2_bt_percent_good,
         beam3_bt_percent_good, beam4_bt_percent_good, ref_layer_min,
         ref_layer_near, ref_layer_far, beam1_ref_layer_velocity,
         beam2_ref_layer_velocity, beam3_ref_layer_velocity,
         beam4_ref_layer_velocity, beam1_ref_correlation, beam2_ref_correlation,
         beam3_ref_correlation, beam4_ref_correlation, beam1_ref_intensity,
         beam2_ref_intensity, beam3_ref_intensity, beam4_ref_intensity,
         beam1_ref_percent_good, beam2_ref_percent_good, beam3_ref_percent_good,
         beam4_ref_percent_good, bt_max_depth, beam1_rssi_amplitude,
         beam2_rssi_amplitude, beam3_rssi_amplitude, beam4_rssi_amplitude,
         bt_gain, beam1_bt_range_msb, beam2_bt_range_msb, beam3_bt_range_msb,
         beam4_bt_range_msb) = \
            unpack('<HHHBBBBHLHHHHhhhhBBBBBBBBBBBBHHHhhhhBBBBBBBBBBBBHBBBBBBBBB', chunk)

        if 1536 != bottom_track_id:
            raise SampleException("bottom_track_id was not equal to 1536")

        self._dvl[Names.BOTTOM_TRACK_ID].append(bottom_track_id)
        self._dvl[Names.BT_PINGS_PER_ENSEMBLE].append(bt_pings_per_ensemble)
        self._dvl[Names.BT_DELAY_BEFORE_REACQUIRE].append(bt_delay_before_reacquire)
        self._dvl[Names.BT_CORR_MAGNITUDE_MIN].append(bt_corr_magnitude_min)
        self._dvl[Names.BT_EVAL_MAGNITUDE_MIN].append(bt_eval_magnitude_min)
        self._dvl[Names.BT_PERCENT_GOOD_MIN].append(bt_percent_good_min)
        self._dvl[Names.BT_MODE].append(bt_mode)
        self._dvl[Names.BT_ERROR_VELOCITY_MAX].append(bt_error_velocity_max)
        self._dvl[Names.BEAM1_BT_RANGE_LSB].append(beam1_bt_range_lsb)
        self._dvl[Names.BEAM2_BT_RANGE_LSB].append(beam2_bt_range_lsb)
        self._dvl[Names.BEAM3_BT_RANGE_LSB].append(beam3_bt_range_lsb)
        self._dvl[Names.BEAM4_BT_RANGE_LSB].append(beam4_bt_range_lsb)
        self._dvl[Names.EASTWARD_BT_VELOCITY].append(eastward_bt_velocity)
        self._dvl[Names.NORTHWARD_BT_VELOCITY].append(northward_bt_velocity)
        self._dvl[Names.UPWARD_BT_VELOCITY].append(upward_bt_velocity)
        self._dvl[Names.ERROR_BT_VELOCITY].append(error_bt_velocity)
        self._dvl[Names.BEAM1_BT_CORRELATION].append(beam1_bt_correlation)
        self._dvl[Names.BEAM2_BT_CORRELATION].append(beam2_bt_correlation)
        self._dvl[Names.BEAM3_BT_CORRELATION].append(beam3_bt_correlation)
        self._dvl[Names.BEAM4_BT_CORRELATION].append(beam4_bt_correlation)
        self._dvl[Names.BEAM1_EVAL_AMP].append(beam1_eval_amp)
        self._dvl[Names.BEAM2_EVAL_AMP].append(beam2_eval_amp)
        self._dvl[Names.BEAM3_EVAL_AMP].append(beam3_eval_amp)
        self._dvl[Names.BEAM4_EVAL_AMP].append(beam4_eval_amp)
        self._dvl[Names.BEAM1_BT_PERCENT_GOOD].append(beam1_bt_percent_good)
        self._dvl[Names.BEAM2_BT_PERCENT_GOOD].append(beam2_bt_percent_good)
        self._dvl[Names.BEAM3_BT_PERCENT_GOOD].append(beam3_bt_percent_good)
        self._dvl[Names.BEAM4_BT_PERCENT_GOOD].append(beam4_bt_percent_good)
        self._dvl[Names.REF_LAYER_MIN].append(ref_layer_min)
        self._dvl[Names.REF_LAYER_NEAR].append(ref_layer_near)
        self._dvl[Names.REF_LAYER_FAR].append(ref_layer_far)
        self._dvl[Names.BEAM1_REF_LAYER_VELOCITY].append(beam1_ref_layer_velocity)
        self._dvl[Names.BEAM2_REF_LAYER_VELOCITY].append(beam2_ref_layer_velocity)
        self._dvl[Names.BEAM3_REF_LAYER_VELOCITY].append(beam3_ref_layer_velocity)
        self._dvl[Names.BEAM4_REF_LAYER_VELOCITY].append(beam4_ref_layer_velocity)
        self._dvl[Names.BEAM1_REF_CORRELATION].append(beam1_ref_correlation)
        self._dvl[Names.BEAM2_REF_CORRELATION].append(beam2_ref_correlation)
        self._dvl[Names.BEAM3_REF_CORRELATION].append(beam3_ref_correlation)
        self._dvl[Names.BEAM4_REF_CORRELATION].append(beam4_ref_correlation)
        self._dvl[Names.BEAM1_REF_INTENSITY].append(beam1_ref_intensity)
        self._dvl[Names.BEAM2_REF_INTENSITY].append(beam2_ref_intensity)
        self._dvl[Names.BEAM3_REF_INTENSITY].append(beam3_ref_intensity)
        self._dvl[Names.BEAM4_REF_INTENSITY].append(beam4_ref_intensity)
        self._dvl[Names.BEAM1_REF_PERCENT_GOOD].append(beam1_ref_percent_good)
        self._dvl[Names.BEAM2_REF_PERCENT_GOOD].append(beam2_ref_percent_good)
        self._dvl[Names.BEAM3_REF_PERCENT_GOOD].append(beam3_ref_percent_good)
        self._dvl[Names.BEAM4_REF_PERCENT_GOOD].append(beam4_ref_percent_good)
        self._dvl[Names.BT_MAX_DEPTH].append(bt_max_depth)
        self._dvl[Names.BEAM1_RSSI_AMPLITUDE].append(beam1_rssi_amplitude)
        self._dvl[Names.BEAM2_RSSI_AMPLITUDE].append(beam2_rssi_amplitude)
        self._dvl[Names.BEAM3_RSSI_AMPLITUDE].append(beam3_rssi_amplitude)
        self._dvl[Names.BEAM4_RSSI_AMPLITUDE].append(beam4_rssi_amplitude)
        self._dvl[Names.BT_GAIN].append(bt_gain)
        self._dvl[Names.BEAM1_BT_RANGE_MSB].append(beam1_bt_range_msb)
        self._dvl[Names.BEAM2_BT_RANGE_MSB].append(beam2_bt_range_msb)
        self._dvl[Names.BEAM3_BT_RANGE_MSB].append(beam3_bt_range_msb)
        self._dvl[Names.BEAM4_BT_RANGE_MSB].append(beam4_bt_range_msb)

    def fill_bt_nans(self):
        """
        If there is no bottom track for this ensemble, fill the bottom track
        portion with nans
        """
        self._dvl[Names.BOTTOM_TRACK_ID].append(np.nan)
        self._dvl[Names.BT_PINGS_PER_ENSEMBLE].append(np.nan)
        self._dvl[Names.BT_DELAY_BEFORE_REACQUIRE].append(np.nan)
        self._dvl[Names.BT_CORR_MAGNITUDE_MIN].append(np.nan)
        self._dvl[Names.BT_EVAL_MAGNITUDE_MIN].append(np.nan)
        self._dvl[Names.BT_PERCENT_GOOD_MIN].append(np.nan)
        self._dvl[Names.BT_MODE].append(np.nan)
        self._dvl[Names.BT_ERROR_VELOCITY_MAX].append(np.nan)
        self._dvl[Names.BEAM1_BT_RANGE_LSB].append(np.nan)
        self._dvl[Names.BEAM2_BT_RANGE_LSB].append(np.nan)
        self._dvl[Names.BEAM3_BT_RANGE_LSB].append(np.nan)
        self._dvl[Names.BEAM4_BT_RANGE_LSB].append(np.nan)
        self._dvl[Names.EASTWARD_BT_VELOCITY].append(np.nan)
        self._dvl[Names.NORTHWARD_BT_VELOCITY].append(np.nan)
        self._dvl[Names.UPWARD_BT_VELOCITY].append(np.nan)
        self._dvl[Names.ERROR_BT_VELOCITY].append(np.nan)
        self._dvl[Names.BEAM1_BT_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM2_BT_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM3_BT_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM4_BT_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM1_EVAL_AMP].append(np.nan)
        self._dvl[Names.BEAM2_EVAL_AMP].append(np.nan)
        self._dvl[Names.BEAM3_EVAL_AMP].append(np.nan)
        self._dvl[Names.BEAM4_EVAL_AMP].append(np.nan)
        self._dvl[Names.BEAM1_BT_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM2_BT_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM3_BT_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM4_BT_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.REF_LAYER_MIN].append(np.nan)
        self._dvl[Names.REF_LAYER_NEAR].append(np.nan)
        self._dvl[Names.REF_LAYER_FAR].append(np.nan)
        self._dvl[Names.BEAM1_REF_LAYER_VELOCITY].append(np.nan)
        self._dvl[Names.BEAM2_REF_LAYER_VELOCITY].append(np.nan)
        self._dvl[Names.BEAM3_REF_LAYER_VELOCITY].append(np.nan)
        self._dvl[Names.BEAM4_REF_LAYER_VELOCITY].append(np.nan)
        self._dvl[Names.BEAM1_REF_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM2_REF_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM3_REF_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM4_REF_CORRELATION].append(np.nan)
        self._dvl[Names.BEAM1_REF_INTENSITY].append(np.nan)
        self._dvl[Names.BEAM2_REF_INTENSITY].append(np.nan)
        self._dvl[Names.BEAM3_REF_INTENSITY].append(np.nan)
        self._dvl[Names.BEAM4_REF_INTENSITY].append(np.nan)
        self._dvl[Names.BEAM1_REF_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM2_REF_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM3_REF_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BEAM4_REF_PERCENT_GOOD].append(np.nan)
        self._dvl[Names.BT_MAX_DEPTH].append(np.nan)
        self._dvl[Names.BEAM1_RSSI_AMPLITUDE].append(np.nan)
        self._dvl[Names.BEAM2_RSSI_AMPLITUDE].append(np.nan)
        self._dvl[Names.BEAM3_RSSI_AMPLITUDE].append(np.nan)
        self._dvl[Names.BEAM4_RSSI_AMPLITUDE].append(np.nan)
        self._dvl[Names.BT_GAIN].append(np.nan)
        self._dvl[Names.BEAM1_BT_RANGE_MSB].append(np.nan)
        self._dvl[Names.BEAM2_BT_RANGE_MSB].append(np.nan)
        self._dvl[Names.BEAM3_BT_RANGE_MSB].append(np.nan)
        self._dvl[Names.BEAM4_BT_RANGE_MSB].append(np.nan)