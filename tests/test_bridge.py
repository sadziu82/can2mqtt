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
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported

from can2mqtt.bridge import can2mqtt, mqtt2can, _can2mqtt_simple_sensor_report

from can2mqtt.home_automation import KeyAction, DigitalOutput, Cover


## fixtures
@pytest.fixture()
def can_mqtt_messages():
    return [
        (Mqtt.message('NODE/69/PING/3/EVENT', '0xDEAD'),
         can.Message(arbitration_id = (Message.PING |
                 Node.can_encode(0x69) |
                 Device.can_encode(3) |
                 Operation.EVENT),
             data=pack('<H', 0xDEAD))),
        (Mqtt.message('NODE/89/DATETIME/7/STATE',
                      json.dumps({"year": 2020, "month": 6, "day": 16,
                                 "hour": 1, "minute": 23, "second": 45, "dayofweek": 2})),
         can.Message(arbitration_id = (Message.DATETIME |
                 Node.can_encode(0x89) |
                 Device.can_encode(7) |
                 Operation.STATE),
             data=pack('<HBBBBBB', 2020, 6, 16, 1, 23, 45, 2))),
        (Mqtt.message('NODE/89/KEY/17/EVENT',
                      json.dumps({"keycode": 0x45, "action": KeyAction.UP.name,
                                 "ar_count": 5, "mp_count": 3})),
         can.Message(arbitration_id = (Message.KEY |
                 Node.can_encode(0x89) |
                 Device.can_encode(0x17) |
                 Operation.EVENT),
             data=pack('<BBBB', 0x45, 2, 5, 3))),
        (Mqtt.message('NODE/69/TEMPERATURE/3/STATE', '12.34'),
         can.Message(arbitration_id = (Message.TEMPERATURE |
                 Node.can_encode(0x69) |
                 Device.can_encode(3) |
                 Operation.STATE),
             data=pack('<f', 12.34))),
        (Mqtt.message('NODE/12/RHUMIDITY/7/STATE', '54.32'),
         can.Message(arbitration_id = (Message.RHUMIDITY |
                 Node.can_encode(0x12) |
                 Device.can_encode(7) |
                 Operation.STATE),
             data=pack('<f', 54.32))),
        (Mqtt.message('NODE/F0/ILLUMINANCE/9/STATE', '127'),
         can.Message(arbitration_id = (Message.ILLUMINANCE |
                 Node.can_encode(0xF0) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=pack('<H', 127))),
        (Mqtt.message('NODE/F0/PRESSURE/9/STATE', '1013'),
         can.Message(arbitration_id = (Message.PRESSURE |
                 Node.can_encode(0xF0) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=pack('<H', 1013))),
        (Mqtt.message('NODE/D4/DIGITAL_OUTPUT/9/STATE',
                      bytes(json.dumps({"state": DigitalOutput.ON.name}), 'utf-8')),
         can.Message(arbitration_id = (Message.DIGITAL_OUTPUT |
                 Node.can_encode(0xD4) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=pack('<B', DigitalOutput.ON.value))),
        (Mqtt.message('NODE/34/COVER/2/STATE',
                      json.dumps({"cmd": Cover.OPEN.name, "position": 30})),
         can.Message(arbitration_id = (Message.COVER |
                 Node.can_encode(0x34) |
                 Device.can_encode(2) |
                 Operation.STATE),
             data=pack('<BB', Cover.OPEN.value, 30))),
    ]


@pytest.fixture()
def mqtt_can_messages():
    return [
        (Mqtt.message('NODE/69/PING/3/QUERY', '0xDEAD'),
         can.Message(arbitration_id = (Message.PING |
                 Node.can_encode(0x69) |
                 Device.can_encode(3) |
                 Operation.QUERY),
             data=pack('<H', 0xDEAD))),
        (Mqtt.message('NODE/89/DATETIME/7/SET',
                      json.dumps({"year": 2020, "month": 6, "day": 16,
                                 "hour": 1, "minute": 23, "second": 45, "dayofweek": 2})),
         can.Message(arbitration_id = (Message.DATETIME |
                 Node.can_encode(0x89) |
                 Device.can_encode(7) |
                 Operation.SET),
             data=pack('<HBBBBBB', 2020, 6, 16, 1, 23, 45, 2))),
        (Mqtt.message('NODE/89/KEY/17/QUERY',
                      json.dumps({"keycode": 0x45, "action": KeyAction.UP.name,
                                 "ar_count": 5, "mp_count": 3})),
         can.Message(arbitration_id = (Message.KEY |
                 Node.can_encode(0x89) |
                 Device.can_encode(0x17) |
                 Operation.QUERY),
             data=pack('<BBBB', 0x45, 2, 5, 3))),
        (Mqtt.message('NODE/D4/DIGITAL_OUTPUT/9/SET',
                      bytes(json.dumps({"cmd": DigitalOutput.ON.name}), 'utf-8')),
         can.Message(arbitration_id = (Message.DIGITAL_OUTPUT |
                 Node.can_encode(0xD4) |
                 Device.can_encode(9) |
                 Operation.SET),
             data=pack('<B', DigitalOutput.ON.value))),
        (Mqtt.message('NODE/34/COVER/2/SET',
                      bytes(json.dumps({"cmd": Cover.OPEN.name,
                                       "position": 30}), 'utf-8')),
         can.Message(arbitration_id = (Message.COVER |
                 Node.can_encode(0x34) |
                 Device.can_encode(2) |
                 Operation.SET),
             data=pack('<BB', Cover.OPEN.value, 30))),
    ]


@pytest.fixture()
def mqtt_can_messages_not_supported():
    return [
        (Mqtt.message('NODE/F0/DISCOVERY/0/QUERY', ''),
         can.Message(arbitration_id = (Message.DISCOVERY |
                 Node.can_encode(0xF0) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=None)),
        (Mqtt.message('NODE/F0/PWM_INPUT/9/SET', '1013'),
         can.Message(arbitration_id = (Message.PWM_INPUT |
                 Node.can_encode(0xF0) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=pack('<H', 1013))),
    ]


@pytest.fixture()
def can_message_discovery():
    return can.Message(arbitration_id = (Message.DISCOVERY |
                 Node.can_encode(0xF0) |
                 Device.can_encode(9) |
                 Operation.STATE),
             data=None)


@pytest.fixture()
def bad_can_messages():
    return [
         can.Message(arbitration_id = 0x12345678,
             data=pack('<f', 12.34)),
    ]


@pytest.fixture()
def bad_mqtt_messages():
    return [
        Mqtt.message('NODE/69/BAD_MSG_TYPE/1/STATE', '12.34'),
        Mqtt.message('NODE/69/temperature/2/STATE', '12.34'),
        Mqtt.message('NODE/69/DISCOVERY/QUERY', None),
        Mqtt.message('NODE/69/TEMPERATURE//STATE', '12.34'),
    ]


def test_can2mqtt_ok(can_mqtt_messages):
    for mqtt_msg, can_frame in can_mqtt_messages:
        print(mqtt_msg.payload)
        print(can2mqtt(can_frame).payload)
        assert mqtt_msg == can2mqtt(can_frame)


def test_can2mqtt_not_supported(mqtt_can_messages_not_supported):
    for mqtt_msg, can_frame in mqtt_can_messages_not_supported:
        with pytest.raises(HomeCanMessageNotSupported):
            can2mqtt(can_frame)


def test_can2mqtt_simple_sensor_report(can_message_discovery):
    with pytest.raises(HomeCanMessageNotSupported):
        _can2mqtt_simple_sensor_report(can_message_discovery)


def test_can2mqtt_bad(bad_can_messages):
    for can_frame in bad_can_messages:
        with pytest.raises(ValueError):
            can2mqtt(can_frame)


def test_mqtt2can_ok(mqtt_can_messages):
    for mqtt_msg, can_frame in mqtt_can_messages:
        m2c = mqtt2can(mqtt_msg)
        assert can_frame.equals(m2c)


def test_mqtt2can_not_supported(mqtt_can_messages_not_supported):
    for mqtt_msg, can_frame in mqtt_can_messages_not_supported:
        with pytest.raises(HomeCanMessageNotSupported):
            assert can_frame == mqtt2can(mqtt_msg)


def test_mqtt2can_bad(bad_mqtt_messages):
    for mqtt_msg in bad_mqtt_messages:
        with pytest.raises(HomeCanMessageError):
            mqtt2can(mqtt_msg)
