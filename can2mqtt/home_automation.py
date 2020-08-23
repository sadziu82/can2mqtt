#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum


##
class KeyAction(IntEnum):

    DOWN        = 0x00
    PRESS       = 0x01
    UP          = 0x02
    MULTIPRESS  = 0x03


##
class DigitalOutput(IntEnum):

    OFF         = 0x00
    ON          = 0x01
    TOGGLE      = 0x02


##
class Cover(IntEnum):

    UNKNOWN      = 0x00
    OPEN         = 0x01
    OPENING      = 0x02
    STOP         = 0x03
    CLOSED       = 0x04     ## same as next on purpose
    CLOSE        = 0x04
    CLOSING      = 0x05
    POSITION     = 0x06     ## same as next on purpose
    SET_POSITION = 0x06
    FAILED       = 0x07

