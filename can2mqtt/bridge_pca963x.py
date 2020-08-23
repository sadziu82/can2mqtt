#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import IntEnum

import re
import can
import sys

from struct import unpack, pack

from can2mqtt.operation import Operation
from can2mqtt.message import Message
from can2mqtt.device import Device
from can2mqtt.node import Node
from can2mqtt.mqtt import Mqtt
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported, HomeCanBridgingForbidden


class PCA963x(object):

    class Channel(IntEnum):
        RED0    = 0x00
        GREEN0  = 0x01
        BLUE0   = 0x02
        AMBER0  = 0x03

        RED1    = 0x04
        GREEN1  = 0x05
        BLUE1   = 0x06
        AMBER1  = 0x07

        RED2    = 0x08
        GREEN2  = 0x09
        BLUE2   = 0x0A
        AMBER2  = 0x0B

        RED3    = 0x0C
        GREEN3  = 0x0D
        BLUE3   = 0x0E
        AMBER3  = 0x0F

        RGB0    = 0x10
        RGB1    = 0x14
        RGB2    = 0x18
        RGB3    = 0x1C

        RGBA0   = 0x20
        RGBA1   = 0x24
        RGBA2   = 0x28
        RGBA3   = 0x2C

    class Command(IntEnum):
        OFF         = 0x00
        ON          = 0x01
        TOGGLE      = 0x02
        PWM         = 0x04


def _can2mqtt_pca963x(can_frame):
    """ Parse HomeCan CAN frame containing commands for PCA963x modules
        data[0] - channel: red, green, blue, amber, rgb, rgba
        data[1] - command: set, brightness, sleep
        data[2-x] - color, brightness, time, etc.
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    ##
    ch = PCA963x.Channel(can_frame.data[0])
    cmd = PCA963x.Command(can_frame.data[1])
    ##
    if ch in [PCA963x.Channel.RED0, PCA963x.Channel.GREEN0,
              PCA963x.Channel.BLUE0, PCA963x.Channel.AMBER0,
              PCA963x.Channel.RED1, PCA963x.Channel.GREEN1,
              PCA963x.Channel.BLUE1, PCA963x.Channel.AMBER1]:
        ##
        if cmd in [PCA963x.Command.OFF, PCA963x.Command.ON,
                   PCA963x.Command.TOGGLE]:
            payload = cmd.name
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, 'SWITCH', op.name),
                    payload)
        elif cmd == PCA963x.Command.PWM_VALUE:
            payload = '{:X}'.format(can_frame.data[2])
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)
        elif cmd == PCA963x.Command.PWM_BRIGHTNESS:
            payload = '{:X}'.format(can_frame.data[2])
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)
        elif cmd == PCA963x.Command.PWM_SLEEP:
            payload = '{:X}'.format(can_frame.data[2] + (can_frame.data[3] << 8))
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)
    elif ch in [PCA963x.Channel.RGB0, PCA963x.Channel.RGB1]:
        ##
        if cmd == PCA963x.Command.PWM_VALUE:
            payload = '{:X},{:X},{:X}'.format(can_frame.data[2], can_frame.data[3],
                                              can_frame.data[4])
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)
        elif cmd == PCA963x.Command.PWM_BRIGHTNESS:
            payload = '{:X}'.format(can_frame.data[2])
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)
        elif cmd == PCA963x.Command.PWM_SLEEP:
            payload = '{:X}'.format(can_frame.data[2] + (can_frame.data[3] << 8))
            return Mqtt.message('NODE/{:X}/{}/{:X}/{}/{}/{}'.format(
                        node_id, msg.name, device_id, ch.name, cmd.name, op.name),
                    payload)

    raise HomeCanMessageNotSupported('pca963x message configuration not '
            'supported by {}'.format(sys._getframe().f_code.co_name))


def _mqtt2can_pca963x(can_eid, msg, channel, payload):
    """ Generate HomeCan CAN frame containing PCA963x command
    """
    if msg != Message.PCA963x:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))

    ## single channel commands
    if PCA963x.Channel[channel].value < PCA963x.Channel.RGB0:
        payload = payload.decode('utf-8')
        if payload in ['OFF', 'ON', 'TOGGLE']:
            data = pack('<BB', PCA963x.Channel[channel].value,
                        PCA963x.Command[payload].value)
        elif re.fullmatch('[0-9]+', payload):
            data = pack('<BBB', PCA963x.Channel[channel].value,
                        PCA963x.Command.PWM.value, int(payload))
        else:
            
            raise HomeCanMessageNotSupported('can message {} type not '
                                             'supported by {}'.format(msg.name,
                                             sys._getframe().f_code.co_name))
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))

    return can.Message(arbitration_id=can_eid, data=data)
