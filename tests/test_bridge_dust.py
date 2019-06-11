#!/usr/bin/env python
# -*- coding: utf-8 -*-

import can
import pytest
import paho.mqtt.client as mqttc #.MQTTMessage

from struct import unpack, pack

from can2mqtt.operation import Operation
from can2mqtt.message import Message
from can2mqtt.device import Device
from can2mqtt.node import Node
from can2mqtt.mqtt import Mqtt
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported

from can2mqtt.bridge import can2mqtt, mqtt2can

from can2mqtt.bridge_dust import DustSensor


## fixtures
@pytest.fixture()
def mqtt_can_messages_valid():
    dust_msgs = [
        ([
            Mqtt.message('NODE/69/DUST/1/{}/{}'.format(
                    DustSensor.Resolution.PM2_5.name, Operation.STATE.name), '5.50'),
            Mqtt.message('NODE/69/DUST/1/{}/{}'.format(
                    DustSensor.Resolution.PM10.name, Operation.STATE.name), '10.10'),
         ],
         can.Message(arbitration_id = (Message.DUST |
                 Node.can_encode(0x69) | Device.can_encode(0x01) | Operation.STATE),
             data=pack('<ff', 5.5, 10.1))),
    ]
    return dust_msgs


@pytest.fixture()
def mqtt_can_messages_invalid():
    dust_msgs = []
    for op in Operation:
        if op == Operation.STATE:
            continue
        dust_msgs.append(([
            Mqtt.message('NODE/69/DUST/1/{}/{}'.format(
                    DustSensor.Resolution.PM2_5.name, Operation.STATE.name), '5.50'),
            Mqtt.message('NODE/69/DUST/1/{}/{}'.format(
                    DustSensor.Resolution.PM10.name, Operation.STATE.name), '10.10'),
         ],
         can.Message(arbitration_id = (Message.DUST |
                 Node.can_encode(0x69) | Device.can_encode(0x01) | op),
             data=pack('<ff', 5.5, 10.1))))
    return dust_msgs


## tests
def test_dust_sensor(mqtt_can_messages_valid):
    for mqtt_msgs, can_frame in mqtt_can_messages_valid:
        msgs = can2mqtt(can_frame)
        assert len(mqtt_msgs) == len(msgs)
        for i in range(len(mqtt_msgs)):
            assert mqtt_msgs[i].topic == msgs[i].topic
            assert mqtt_msgs[i].payload == msgs[i].payload


def test_dust_sensor_invalid_frame(mqtt_can_messages_invalid):
    for mqtt_msgs, can_frame in mqtt_can_messages_invalid:
        with pytest.raises(HomeCanMessageNotSupported):
            msgs = can2mqtt(can_frame)
