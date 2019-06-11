#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import can
import sys

from struct import unpack, pack

from can2mqtt.operation import Operation
from can2mqtt.message import Message
from can2mqtt.device import Device
from can2mqtt.node import Node
from can2mqtt.mqtt import Mqtt
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported


def can2mqtt(can_frame):
    """ Convert CAN frame into MQTT message
    """
    msg = Message.can_decode(can_frame.arbitration_id)
    if msg in [Message.TEMPERATURE, Message.RHUMIDITY,
            Message.ILLUMINANCE, Message.PRESSURE]:
        mqtt_msg = _can2mqtt_simple_sensor_report(can_frame)
    elif msg in [Message.DUST]:
        from can2mqtt.bridge_dust import _can2mqtt_dust
        mqtt_msg = _can2mqtt_dust(can_frame)
    elif msg in [Message.PCA9633, Message.PCA9634]:
        from can2mqtt.bridge_pca963x import _can2mqtt_pca963x
        mqtt_msg = _can2mqtt_pca963x(can_frame)
    else:
        raise HomeCanMessageNotSupported('can message {} type not yet '
                'supported'.format(msg.name))
    return mqtt_msg


def _can2mqtt_simple_sensor_report(can_frame):
    """ Parse HomeCan CAN frame containing simple sensor message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg in [Message.TEMPERATURE, Message.RHUMIDITY]:
        raw_payload, = unpack('<f', can_frame.data)
        payload = '{:0.2f}'.format(raw_payload)
    elif msg in [Message.ILLUMINANCE, Message.PRESSURE]:
        raw_payload, = unpack('<H', can_frame.data)
        payload = '{:d}'.format(raw_payload)
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                node_id, msg.name, device_id, op.name),
            payload)


def mqtt2can(mqtt_msg):
    """ Convert MQTT message into CAN frame
    """
    match = re.match(r'^NODE/(?P<node>[0-9a-fA-F]+)/'
            '(?P<msg>[^/]+)/(?P<dev>[0-9a-fA-F]+)/'
            '((?P<extra>\S+)/)?(?P<op>[^/]+)$',
            mqtt_msg.topic)
    if not match:
        raise HomeCanMessageError('bad mqtt message')
    ## base format seems ok, extract parts for further processing
    node = match.group('node')
    dev = match.group('dev')
    try:
        msg = Message.mqtt_decode(match.group('msg'))
    except KeyError:
        raise HomeCanMessageError('wrong mqtt message type')
    op = Operation[match.group('op')]

    ## FIXME should we translate all messages back and forth?
    #if op not in [HC_MESSAGE.QUERY, HC_MESSAGE.SET]:
    #    raise HomeCanMessageError('wrong mqtt message type')`

    ## calculate CAN extended id
    can_eid = msg | Node.mqtt2can(node) | Device.mqtt2can(dev) | op
    ## prepare frame data based on msg type
    if msg in [Message.TEMPERATURE, Message.RHUMIDITY,
            Message.ILLUMINANCE, Message.PRESSURE]:
        can_frame = _mqtt2can_simple_sensor(can_eid, msg, mqtt_msg.payload)
    elif msg in [Message.DUST]:
        from can2mqtt.bridge_dust import _mqtt2can_dust
        can_frame = _mqtt2can_dust(can_eid, msg, mqtt_msg.payload)
    else:
        raise HomeCanMessageNotSupported('mqtt message {} not yet supported'.
                format(msg.name))
    
    return can_frame


def _mqtt2can_simple_sensor(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing simple sensor message
    """
    if msg in [Message.TEMPERATURE, Message.RHUMIDITY]:
        data = pack('<f', float(payload))
    elif msg in [Message.ILLUMINANCE, Message.PRESSURE]:
        data = pack('<H', int(payload))
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)
