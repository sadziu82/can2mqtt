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
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported, HomeCanBridgingForbidden

from can2mqtt.bridge import can2mqtt, mqtt2can, _can2mqtt_simple_sensor_report

from can2mqtt.bridge_pca963x import PCA963x


## fixtures
@pytest.fixture()
def mqtt_can_messages():
    pca963x_switch_msgs = []
    for op in [Operation.SET]:
        pca963x_switch_msgs.append(
            (Mqtt.message('NODE/69/PCA963x/3/AMBER0/{}'.format(op.name),
                          PCA963x.Command.TOGGLE.name),
             can.Message(arbitration_id = (Message.PCA963x |
                     Node.can_encode(0x69) | Device.can_encode(0x03) | op),
                 data=pack('<BB', PCA963x.Channel.AMBER0, PCA963x.Command.TOGGLE)))
        )

    return pca963x_switch_msgs


def test_pca9633_mqtt2can_on_off_toggle(mqtt_can_messages):
    for mqtt_msg, can_frame in mqtt_can_messages:
        m2c = mqtt2can(mqtt_msg)
        assert can_frame.equals(m2c)
