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

from can2mqtt.bridge import can2mqtt, mqtt2can, _can2mqtt_simple_sensor_report

from can2mqtt.bridge_pca963x import PCA963x


## fixtures
@pytest.fixture()
def mqtt_can_messages():
    pca9633_switch_msgs = []
    for op in Operation:
        pca9633_switch_msgs.append(
            (Mqtt.message('NODE/69/PCA9633/3/AMBER0/SWITCH/{}'.format(op.name),
                          PCA963x.Command.SWITCH_TOGGLE.name),
             can.Message(arbitration_id = (Message.PCA9633 |
                     Node.can_encode(0x69) | Device.can_encode(0x03) | op),
                 data=pack('<BB', PCA963x.Channel.AMBER0, PCA963x.Command.SWITCH_TOGGLE)))
        )

    pca9633_pwm_msgs = []
    for op in Operation:
        pca9633_pwm_msgs.append(
            (Mqtt.message('NODE/69/PCA9633/3/BLUE0/PWM_VALUE/{}'.format(op.name),
                          'A5'),
             can.Message(arbitration_id = (Message.PCA9633 |
                     Node.can_encode(0x69) | Device.can_encode(0x03) | op),
                 data=pack('<BBB', PCA963x.Channel.BLUE0, PCA963x.Command.PWM_VALUE, 0xA5)))
        )
        pca9633_pwm_msgs.append(
            (Mqtt.message('NODE/5A/PCA9633/3/BLUE0/PWM_BRIGHTNESS/{}'.format(op.name),
                          '40'),
             can.Message(arbitration_id = (Message.PCA9633 |
                     Node.can_encode(0x5A) | Device.can_encode(0x03) | op),
                 data=pack('<BBB', PCA963x.Channel.BLUE0, PCA963x.Command.PWM_BRIGHTNESS, 0x40)))
        )
        pca9633_pwm_msgs.append(
            (Mqtt.message('NODE/5B/PCA9633/3/BLUE0/PWM_SLEEP/{}'.format(op.name),
                          'E10'),
             can.Message(arbitration_id = (Message.PCA9633 |
                     Node.can_encode(0x5B) | Device.can_encode(0x03) | op),
                 data=pack('<BBH', PCA963x.Channel.BLUE0, PCA963x.Command.PWM_SLEEP, 0xE10)))
        )

    pca9633_rgb_msgs = []
    #for op in Operation:
    #    pca9633_rgb_msgs.append(
    #        (Mqtt.message('NODE/69/PCA9633/3/RGB0/PWM_VALUE/{}'.format(op.name),
    #                      PCA963x.Command.PWM_VALUE),
    #         can.Message(arbitration_id = (Message.PCA9633 |
    #                 Node.can_encode(0x69) | Device.can_encode(0x03) | op),
    #             data=pack('<BBBBB', PCA963x.Channel.AMBER0, PCA963x.Command.PWM_VALUE),
    #             extended_id=True))
    #    )

    pca9633_rgba_msgs = []
    #for op in Operation:
    #    pca9633_rgba_msgs.append(
    #        (Mqtt.message('NODE/69/PCA9633/3/RGB0/PWM_VALUE/{}'.format(op.name),
    #                      PCA963x.Command.SWITCH_TOGGLE.name),
    #         can.Message(arbitration_id = (Message.PCA9633 |
    #                 Node.can_encode(0x69) | Device.can_encode(0x03) | op),
    #             data=pack('<BB', PCA963x.Channel.AMBER0, PCA963x.Command.SWITCH_TOGGLE),
    #             extended_id=True))
    #    )

    pca9634_switch_msgs = []
    #for op in Operation:
    #    pca9634_switch_msgs.append(
    #        (Mqtt.message('NODE/69/PCA9634/3/GREEN1/SWITCH/{}'.format(op.name),
    #                      PCA963x.Command.SWITCH_TOGGLE.name),
    #         can.Message(arbitration_id = (Message.PCA9634 |
    #                 Node.can_encode(0x69) | Device.can_encode(0x03) | op),
    #             data=pack('<BB', PCA963x.Channel.GREEN1, PCA963x.Command.SWITCH_TOGGLE),
    #             extended_id=True))
    #    )

    return pca9633_switch_msgs + pca9633_pwm_msgs + pca9633_rgb_msgs + pca9633_rgba_msgs
    ##### return [
    #####     (Mqtt.message('NODE/A5/PCA9634/77/BLUE1/SWITCH/STATE',
    #####                   PCA963x.Command.SWITCH_ON.name),
    #####      can.Message(arbitration_id = (Message.PCA9634 |
    #####              Node.can_encode(0xA5) |
    #####              Device.can_encode(0x77) |
    #####              Operation.STATE),
    #####          data=pack('<BB', PCA963x.Channel.BLUE1, PCA963x.Command.SWITCH_ON),
    #####          extended_id=True)),
    #####     (Mqtt.message('NODE/69/PCA9633/3/RED0/PWM/SET',
    #####                   '234'),
    #####      can.Message(arbitration_id = (Message.PCA9633 |
    #####              Node.can_encode(0x69) |
    #####              Device.can_encode(3) |
    #####              Operation.SET),
    #####          data=pack('<BBB', PCA963x.Channel.RED0, PCA963x.Command.PWM_VALUE, 0x80),
    #####          extended_id=True)),
    #####     (Mqtt.message('NODE/A5/PCA9633/78/RGB0/PWM/SET',
    #####                   '12,89,AB'),
    #####      can.Message(arbitration_id = (Message.PCA9633 |
    #####              Node.can_encode(0xA5) |
    #####              Device.can_encode(0x78) |
    #####              Operation.SET),
    #####          data=pack('<BBBBB', PCA963x.Channel.RGB0, PCA963x.Command.PWM_VALUE,
    #####              0x12, 0x89, 0xAB),
    #####          extended_id=True)),
    ##### ]


def test_pca9633_pwm_set(mqtt_can_messages):
    for mqtt_msg, can_frame in mqtt_can_messages:
        msg = can2mqtt(can_frame)
        #print(msg.topic, msg.payload)
        #print(mqtt_msg.topic, mqtt_msg.payload)
        assert mqtt_msg.topic == msg.topic
        assert mqtt_msg.payload == msg.payload
