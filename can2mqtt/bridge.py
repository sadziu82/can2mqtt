#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import can
import sys
import json

from struct import unpack, pack

from can2mqtt.operation import Operation
from can2mqtt.message import Message
from can2mqtt.device import Device
from can2mqtt.node import Node
from can2mqtt.mqtt import Mqtt
from can2mqtt.excp import HomeCanMessageError, HomeCanMessageNotSupported, HomeCanBridgingForbidden

from can2mqtt.home_automation import KeyAction, DigitalOutput, Cover

def can2mqtt(can_frame):
    """ Convert CAN frame into MQTT message
    """
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)

    if op not in [Operation.STATE, Operation.EVENT]:
        raise HomeCanBridgingForbidden('{} may not be translated from CAN into MQTT'.format(op.name))

    if msg == Message.PING:
        mqtt_msg = _can2mqtt_ping(can_frame)
    elif msg == Message.DATETIME:
        mqtt_msg = _can2mqtt_datetime(can_frame)
    elif msg == Message.KEY:
        mqtt_msg = _can2mqtt_key(can_frame)
    elif msg in [Message.TEMPERATURE, Message.RHUMIDITY,
            Message.ILLUMINANCE, Message.PRESSURE]:
        mqtt_msg = _can2mqtt_simple_sensor_report(can_frame)
    elif msg == Message.DUST:
        from can2mqtt.bridge_dust import _can2mqtt_dust
        mqtt_msg = _can2mqtt_dust(can_frame)
    elif msg == Message.DIGITAL_OUTPUT:
        mqtt_msg = _can2mqtt_digital_output(can_frame)
    elif msg == Message.PCA963x:
        from can2mqtt.bridge_pca963x import _can2mqtt_pca963x
        mqtt_msg = _can2mqtt_pca963x(can_frame)
    elif msg  == Message.COVER:
        mqtt_msg = _can2mqtt_cover(can_frame)
    else:
        raise HomeCanMessageNotSupported('can message {} type not yet '
                'supported'.format(msg.name))
    return mqtt_msg


def _can2mqtt_ping(can_frame):
    """ Parse HomeCan CAN frame containing ping message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg == Message.PING:
        raw_payload, = unpack('<H', can_frame.data)
        payload = '0x{:4X}'.format(raw_payload)
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                node_id, msg.name, device_id, op.name),
            payload)


def _can2mqtt_datetime(can_frame):
    """ Parse HomeCan CAN frame containing date/time message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg == Message.DATETIME:
        year, month, day, hour, minute, second, weekday = unpack('<HBBBBBB', can_frame.data)
        payload = json.dumps({"year": year, "month": month, "day": day,
                             "hour": hour, "minute": minute, "second": second,
                             "dayofweek": weekday})
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                node_id, msg.name, device_id, op.name),
            payload)


def _can2mqtt_key(can_frame):
    """ Parse HomeCan CAN frame containing key message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg == Message.KEY:
        keycode, key_action_raw, ar_count, mp_count = unpack('<BBBB', can_frame.data)
        key_action = KeyAction(key_action_raw).name
        payload = json.dumps({"keycode": keycode, "action": key_action,
                             "ar_count": ar_count, "mp_count": mp_count})
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                node_id, msg.name, device_id, op.name),
            payload)


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


def _can2mqtt_digital_output(can_frame):
    """ Parse HomeCan CAN frame containing digital output message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg == Message.DIGITAL_OUTPUT:
        cmd_raw, = unpack('<B', can_frame.data)
        cmd = DigitalOutput(cmd_raw).name
        payload = bytes(json.dumps({"state": cmd}), 'utf-8')
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                node_id, msg.name, device_id, op.name),
            payload)


def _can2mqtt_cover(can_frame):
    """ Parse HomeCan CAN frame containing cover message
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    op = Operation.can_decode(can_frame.arbitration_id)
    if msg == Message.COVER:
        cmd_raw, position, = unpack('<BB', can_frame.data)
        cmd = Cover(cmd_raw).name
        payload = json.dumps({"cmd": cmd, "position": position})
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

    if op not in [Operation.QUERY, Operation.SET, Operation.RESET]:
        raise HomeCanBridgingForbidden('{} may not be translated from MQTT into CAN'.format(op.name))

    ## FIXME should we translate all messages back and forth?
    #if op not in [HC_MESSAGE.QUERY, HC_MESSAGE.SET]:
    #    raise HomeCanMessageError('wrong mqtt message type')`

    ## calculate CAN extended id
    can_eid = msg | Node.mqtt2can(node) | Device.mqtt2can(dev) | op
    ## prepare frame data based on msg type
    if msg == Message.PING:
        can_frame = _mqtt2can_ping(can_eid, msg, mqtt_msg.payload)
    elif msg == Message.DATETIME:
        can_frame = _mqtt2can_datetime(can_eid, msg, mqtt_msg.payload)
    elif msg == Message.KEY:
        can_frame = _mqtt2can_key(can_eid, msg, mqtt_msg.payload)
    elif msg in [Message.TEMPERATURE, Message.RHUMIDITY,
            Message.ILLUMINANCE, Message.PRESSURE]:
        can_frame = _mqtt2can_simple_sensor(can_eid, msg, mqtt_msg.payload)
    elif msg in [Message.DUST]:
        from can2mqtt.bridge_dust import _mqtt2can_dust
        can_frame = _mqtt2can_dust(can_eid, msg, mqtt_msg.payload)
    elif msg == Message.DIGITAL_OUTPUT:
        can_frame = _mqtt2can_digital_output(can_eid, msg, mqtt_msg.payload)
    elif msg == Message.PCA963x:
        from can2mqtt.bridge_pca963x import _mqtt2can_pca963x
        extra = match.group('extra')
        can_frame = _mqtt2can_pca963x(can_eid, msg, extra, mqtt_msg.payload)
    elif msg == Message.COVER:
        can_frame = _mqtt2can_cover(can_eid, msg, mqtt_msg.payload)
    else:
        raise HomeCanMessageNotSupported('mqtt message {} not yet supported'.
                format(msg.name))
    
    return can_frame


def _mqtt2can_ping(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing ping message
    """
    if msg == Message.PING:
        data = pack('<H', int(payload, 0x10))
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)


def _mqtt2can_datetime(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing date/time message
    """
    if msg == Message.DATETIME:
        dt = json.loads(payload)
        data = pack('<HBBBBBB', dt['year'], dt['month'], dt['day'],
                    dt['hour'], dt['minute'], dt['second'],
                    dt['dayofweek'])
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)


def _mqtt2can_key(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing key message
    """
    if msg == Message.KEY:
        key = json.loads(payload)
        data = pack('<BBBB', key['keycode'], KeyAction[key['action']], key['ar_count'], key['mp_count'])
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)


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


def _mqtt2can_digital_output(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing digital output message
    """
    if msg == Message.DIGITAL_OUTPUT:
        js = json.loads(payload.decode('utf-8'))
        data = pack('<B', DigitalOutput[js['cmd']].value)
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)


def _mqtt2can_cover(can_eid, msg, payload):
    """ Generate HomeCan CAN frame containing cover message
    """
    if msg == Message.COVER:
        js = json.loads(payload.decode('utf-8'))
        data = pack('<BB', Cover[js['cmd']].value, js['position'])
    else:
        raise HomeCanMessageNotSupported('can message {} type not '
                'supported by {}'.format(msg.name,
                    sys._getframe().f_code.co_name))
    return can.Message(arbitration_id=can_eid, data=data)
