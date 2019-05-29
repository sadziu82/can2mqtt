#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


##
_hc_operation_shift = 18
_hc_operation_mask  = 0x07 << _hc_operation_shift

##
def _encode(op_id):
    return ((op_id << _hc_operation_shift) & _hc_operation_mask)

##
class Operation(IntEnum):

    QUERY     = _encode(0x00)
    SET       = _encode(0x01)
    STATE     = _encode(0x02)
    EVENT     = _encode(0x03)
    RESERVED1 = _encode(0x04)
    RESERVED2 = _encode(0x05)
    RESERVED3 = _encode(0x06)
    RESET     = _encode(0x07)

    @staticmethod
    def mqtt_decode(mqtt_op):
        return Operation[mqtt_op]

    @staticmethod
    def mqtt2can(mqtt_op):
        return Operation.mqtt_decode(mqtt_op).value

    @staticmethod
    def can_decode(can_eid):
        op_id = can_eid & _hc_operation_mask
        return Operation(op_id)

    @staticmethod
    def can2mqtt(can_eid):
        return Operation.can_decode(can_eid).name
