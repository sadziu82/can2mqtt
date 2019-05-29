#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from can2mqtt.message import Message


## fixtures
@pytest.fixture()
def hc_messages_ok():
   return [
        (key, msg.value) for key, msg in Message.__members__.items()
    ]


## tests
def test_message_mqtt2can(hc_messages_ok):
    for mqtt, can in hc_messages_ok:
        assert Message.mqtt2can(mqtt) == can

def test_message_can2mqtt(hc_messages_ok):
    for mqtt, can in hc_messages_ok:
        assert Message.can2mqtt(can) == mqtt

def test_message_mqtt_can_decode(hc_messages_ok):
    for mqtt, can in hc_messages_ok:
        assert Message.mqtt_decode(mqtt) == Message.can_decode(can)
