#!/usr/bin/env python
# -*- coding: utf-8 -*-

import can
import json
import pytest
import paho.mqtt.client as mqttc #.MQTTMessage

from struct import unpack, pack

from can2mqtt.operation import Operation
from can2mqtt.message import Message
from can2mqtt.device import Device
from can2mqtt.node import Node
from can2mqtt.mqtt import Mqtt
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported, HomeCanBridgingForbidden

from can2mqtt.bridge import can2mqtt, mqtt2can


## fixtures
@pytest.fixture()
def can2mqtt_messages_valid():
    return [
        (Mqtt.message('NODE/69/DUST/1/STATE',
            bytes(json.dumps({"pm2.5": 5.5, "pm10": 10.1}), 'utf-8')),
         can.Message(arbitration_id = (Message.DUST |
                 Node.can_encode(0x69) | Device.can_encode(0x01) | Operation.STATE),
             data=pack('<ff', 5.5, 10.1))),
    ]


@pytest.fixture()
def can2mqtt_messages_invalid():
    return [
        (Mqtt.message('NODE/69/DUST/0/SET',
            bytes(json.dumps({"pm2.5": 0, "pm10": 0}), 'utf-8')),
         can.Message(arbitration_id = (Message.DUST |
                 Node.can_encode(0x69) | Device.can_encode(0x01) | Operation.SET),
             data=pack('<ff', 0.001, 0.001))),
    ]


## tests
def test_dust_sensor(can2mqtt_messages_valid):
    for mqtt_msg, can_frame in can2mqtt_messages_valid:
        assert mqtt_msg == can2mqtt(can_frame)


def test_dust_sensor_invalid_frame(can2mqtt_messages_invalid):
    for mqtt_msg, can_frame in can2mqtt_messages_invalid:
        with pytest.raises(HomeCanBridgingForbidden):
            msg = can2mqtt(can_frame)
