#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


#
_hc_message_shift = 21
_hc_message_mask = 0xFF << _hc_message_shift


##
def _encode(msg_id):
    return ((msg_id << _hc_message_shift) & _hc_message_mask)


##
class Message(IntEnum):

    DATETIME            = _encode(0x001)
    KEYBOARD            = _encode(0x002)
    TEMPERATURE         = _encode(0x010)
    RHUMIDITY           = _encode(0x011)
    ILLUMINANCE         = _encode(0x012)
    PRESSURE            = _encode(0x013)
    DUST                = _encode(0x014)
    ANALOG_OUTPUT       = _encode(0x020)
    DIGITAL_OUTPUT      = _encode(0x021)
    PWM_OUTPUT          = _encode(0x022)
    RGB_OUTPUT          = _encode(0x023)
    RGBA_OUTPUT         = _encode(0x024)
    ANALOG_INPUT        = _encode(0x030)
    DIGITAL_INPUT       = _encode(0x031)
    PWM_INPUT           = _encode(0x032)
    PCA9633             = _encode(0x040)
    PCA9634             = _encode(0x041)
    GESTURE             = _encode(0x050)
    MOTION_SENSOR       = _encode(0x0A0)
    DISCOVERY           = _encode(0x0D0)
    FIRMWARE            = _encode(0x0E0)
    ALARM               = _encode(0x0F0)
    INTRUSION           = _encode(0x0F1)

    @staticmethod
    def mqtt_decode(mqtt_op):
        return Message[mqtt_op]

    @staticmethod
    def mqtt2can(mqtt_op):
        return Message.mqtt_decode(mqtt_op).value

    @staticmethod
    def can_decode(can_eid):
        op_id = can_eid & _hc_message_mask
        return Message(op_id)

    @staticmethod
    def can2mqtt(can_eid):
        return Message.can_decode(can_eid).name
