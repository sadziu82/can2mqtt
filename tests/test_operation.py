#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from can2mqtt.operation import Operation


## fixtures
@pytest.fixture()
def hc_operations_ok():
   return [
        (key, msg.value) for key, msg in Operation.__members__.items()
    ]


## tests
def test_operation_mqtt2can(hc_operations_ok):
    for mqtt, can in hc_operations_ok:
        assert Operation.mqtt2can(mqtt) == can

def test_operation_can2mqtt(hc_operations_ok):
    for mqtt, can in hc_operations_ok:
        assert Operation.can2mqtt(can) == mqtt

def test_operation_mqtt_can_decode(hc_operations_ok):
    for mqtt, can in hc_operations_ok:
        assert Operation.mqtt_decode(mqtt) == Operation.can_decode(can)
