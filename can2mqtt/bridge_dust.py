#!/usr/bin/env python
# -*- coding: utf-8 -*-


from enum import IntEnum

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


def _can2mqtt_dust(can_frame):
    """ Parse HomeCan CAN frame containing data from dust sensors
        data[0-3] - data: pm2.5
        data[4-7] - data: pm10
    """
    node_id = Node.can_decode(can_frame.arbitration_id)
    device_id = Device.can_decode(can_frame.arbitration_id)
    msg = Message.can_decode(can_frame.arbitration_id)
    ##
    op = Operation.can_decode(can_frame.arbitration_id)
    if op != Operation.STATE:
        raise HomeCanBridgingForbidden('operation {} not supported for {} '
                'messages'.format(op.name, msg.name))
    ##
    pm2_5, pm10, = unpack('<ff', can_frame.data)
    ##
    return Mqtt.message('NODE/{:X}/{}/{:X}/{}'.format(
                    node_id, msg.name, device_id, Operation.STATE.name),
            bytes(json.dumps({"pm2.5": round(pm2_5, 2),
                              "pm10": round(pm10, 2)}),
                  'utf-8'))
