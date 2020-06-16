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
