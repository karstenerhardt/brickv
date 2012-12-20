# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2012-12-20.      #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generator git on tinkerforge.com                   #
#############################################################

try:
    from collections import namedtuple
except ImportError:
    try:
        from .ip_connection import namedtuple
    except ValueError:
        from ip_connection import namedtuple

try:
    from .ip_connection import Device, IPConnection, Error
except ValueError:
    from ip_connection import Device, IPConnection, Error

GetCoordinates = namedtuple('Coordinates', ['latitude', 'ns', 'longitude', 'ew', 'pdop', 'hdop', 'vdop', 'epe'])
GetStatus = namedtuple('Status', ['fix', 'satellites_view', 'satellites_used'])
GetAltitude = namedtuple('Altitude', ['altitude', 'geoidal_separation'])
GetMotion = namedtuple('Motion', ['course', 'speed'])
GetDateTime = namedtuple('DateTime', ['date', 'time'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletGPS(Device):
    """
    Device for receiving GPS position
    """

    DEVICE_IDENTIFIER = 222

    CALLBACK_COORDINATES = 17
    CALLBACK_STATUS = 18
    CALLBACK_ALTITUDE = 19
    CALLBACK_MOTION = 20
    CALLBACK_DATE_TIME = 21

    FUNCTION_GET_COORDINATES = 1
    FUNCTION_GET_STATUS = 2
    FUNCTION_GET_ALTITUDE = 3
    FUNCTION_GET_MOTION = 4
    FUNCTION_GET_DATE_TIME = 5
    FUNCTION_RESTART = 6
    FUNCTION_SET_COORDINATES_CALLBACK_PERIOD = 7
    FUNCTION_GET_COORDINATES_CALLBACK_PERIOD = 8
    FUNCTION_SET_STATUS_CALLBACK_PERIOD = 9
    FUNCTION_GET_STATUS_CALLBACK_PERIOD = 10
    FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD = 11
    FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD = 12
    FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD = 13
    FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD = 14
    FUNCTION_SET_MOTION_CALLBACK_PERIOD = 15
    FUNCTION_GET_MOTION_CALLBACK_PERIOD = 16
    FUNCTION_GET_IDENTITY = 255

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon)

        self.api_version = (1, 0, 0)

        self.response_expected[BrickletGPS.FUNCTION_GET_COORDINATES] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_GET_STATUS] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_GET_ALTITUDE] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_GET_MOTION] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_GET_DATE_TIME] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_RESTART] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_SET_COORDINATES_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_COORDINATES_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_SET_STATUS_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_STATUS_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.FUNCTION_SET_MOTION_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_MOTION_CALLBACK_PERIOD] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletGPS.CALLBACK_COORDINATES] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPS.CALLBACK_STATUS] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPS.CALLBACK_ALTITUDE] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPS.CALLBACK_MOTION] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPS.CALLBACK_DATE_TIME] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_FALSE
        self.response_expected[BrickletGPS.FUNCTION_GET_IDENTITY] = BrickletGPS.RESPONSE_EXPECTED_ALWAYS_TRUE

        self.callback_formats[BrickletGPS.CALLBACK_COORDINATES] = 'I c I c H H H H'
        self.callback_formats[BrickletGPS.CALLBACK_STATUS] = 'B B B'
        self.callback_formats[BrickletGPS.CALLBACK_ALTITUDE] = 'I I'
        self.callback_formats[BrickletGPS.CALLBACK_MOTION] = 'I I'
        self.callback_formats[BrickletGPS.CALLBACK_DATE_TIME] = 'I I'

    def get_coordinates(self):
        """
        
        """
        return GetCoordinates(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_COORDINATES, (), '', 'I c I c H H H H'))

    def get_status(self):
        """
        
        """
        return GetStatus(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_STATUS, (), '', 'B B B'))

    def get_altitude(self):
        """
        
        """
        return GetAltitude(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_ALTITUDE, (), '', 'I I'))

    def get_motion(self):
        """
        
        """
        return GetMotion(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_MOTION, (), '', 'I I'))

    def get_date_time(self):
        """
        
        """
        return GetDateTime(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_DATE_TIME, (), '', 'I I'))

    def restart(self, restart_type):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_RESTART, (restart_type,), 'B', '')

    def set_coordinates_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_SET_COORDINATES_CALLBACK_PERIOD, (period,), 'I', '')

    def get_coordinates_callback_period(self):
        """
        Returns the period as set by :func:`SetCoordinatesCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_COORDINATES_CALLBACK_PERIOD, (), '', 'I')

    def set_status_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_SET_STATUS_CALLBACK_PERIOD, (period,), 'I', '')

    def get_status_callback_period(self):
        """
        Returns the period as set by :func:`SetStatusCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_STATUS_CALLBACK_PERIOD, (), '', 'I')

    def set_altitude_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_SET_ALTITUDE_CALLBACK_PERIOD, (period,), 'I', '')

    def get_altitude_callback_period(self):
        """
        Returns the period as set by :func:`SetAltitudeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_ALTITUDE_CALLBACK_PERIOD, (), '', 'I')

    def set_date_time_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_SET_DATE_TIME_CALLBACK_PERIOD, (period,), 'I', '')

    def get_date_time_callback_period(self):
        """
        Returns the period as set by :func:`SetDateTimeCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_DATE_TIME_CALLBACK_PERIOD, (), '', 'I')

    def set_motion_callback_period(self, period):
        """
        
        """
        self.ipcon.send_request(self, BrickletGPS.FUNCTION_SET_MOTION_CALLBACK_PERIOD, (period,), 'I', '')

    def get_motion_callback_period(self):
        """
        Returns the period as set by :func:`SetMotionCallbackPeriod`.
        """
        return self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_MOTION_CALLBACK_PERIOD, (), '', 'I')

    def get_identity(self):
        """
        .. versionadded:: 2.0.0~(Plugin)
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletGPS.FUNCTION_GET_IDENTITY, (), '', '8s 8s c 3B 3B H'))

    def register_callback(self, id, callback):
        """
        Registers a callback with ID *id* to the function *callback*.
        """
        self.registered_callbacks[id] = callback

GPS = BrickletGPS # for backward compatibility
