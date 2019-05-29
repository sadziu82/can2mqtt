#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


##
_hc_device_mask  = 0xFF


##
class Device(object):

    @staticmethod
    def mqtt_decode(mqtt_dev):
        return int(mqtt_dev, 0x10)

    @staticmethod
    def mqtt2can(mqtt_dev):
        return Device.mqtt_decode(mqtt_dev)

    @staticmethod
    def can_decode(can_eid):
        dev_id = can_eid & _hc_device_mask
        return dev_id

    @staticmethod
    def can_encode(dev_id):
        return (dev_id & _hc_device_mask)

    @staticmethod
    def can2mqtt(can_eid):
        return '{:X}'.format(Device.can_decode(can_eid))
