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

    PING                = _encode(0x00)
    DATETIME            = _encode(0x01)
    KEY                 = _encode(0x02)
    ## sensors
    TEMPERATURE         = _encode(0x10)
    RHUMIDITY           = _encode(0x11)
    ILLUMINANCE         = _encode(0x12)
    PRESSURE            = _encode(0x13)
    MOISTURE            = _encode(0x14)
    DUST                = _encode(0x15)
    GESTURE             = _encode(0x16)
    MOTION              = _encode(0x17)
    ## inputs
    ANALOG_INPUT        = _encode(0x30)
    DIGITAL_INPUT       = _encode(0x31)
    PWM_INPUT           = _encode(0x32)
    ## outputs
    ANALOG_OUTPUT       = _encode(0x38)
    DIGITAL_OUTPUT      = _encode(0x39)
    PWM_OUTPUT          = _encode(0x3A)
    ## lights
    WS2812B             = _encode(0x40)
    PCA963x             = _encode(0x41)
    ## complex devices
    COVER               = _encode(0x60)
    ##
    DISCOVERY           = _encode(0xD0)
    FIRMWARE            = _encode(0xE0)
    ALARM               = _encode(0xF0)
    INTRUSION           = _encode(0xF1)

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
