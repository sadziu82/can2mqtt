#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from can2mqtt.device import Device


## fixtures
@pytest.fixture()
def hc_devices():
   return [
        ('12', 0x12),
        ('69', 0x69),
    ]


## tests
def test_device_mqtt2can(hc_devices):
    for mqtt, can in hc_devices:
        assert Device.mqtt2can(mqtt) == can

def test_device_can2mqtt(hc_devices):
    for mqtt, can in hc_devices:
        assert Device.can2mqtt(can) == mqtt
