#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
import os
import can
import configparser
import paho.mqtt.client as mqtt_client

from time import time

from can2mqtt.logging import logger
from can2mqtt.excp import HomeCanMessageError
from can2mqtt.bridge import can2mqtt, mqtt2can

import logging


##
def on_mqtt_message(client, can_bus, mqtt_msg):
    try:
        logger.debug('got message on {}'.format(mqtt_msg.topic))
        can_msg = mqtt2can(mqtt_msg)
        can_bus.send(can_msg)
    except HomeCanMessageError as e:
        logger.error('mqtt message handling error on topic {}: {}'.format(
                    mqtt_msg.topic, e))
    except Exception as e:
        print('*** {} {}'.format(str(mqtt_msg.topic), e))
        #pass

##
def config_read():
    config = configparser.ConfigParser()
    config.read([
                'can2mqtt.ini',
                os.path.expanduser('~/.can2mqtt.ini'),
                '/etc/default/can2mqtt.ini',
    ])
    return config


##
if __name__ == "__main__":
    ##
    config = config_read()
    ##
    logger.setLevel(logging.INFO)
    ##
    can_bus = can.interface.Bus(channel=config['canbus']['channel'],
                                bustype=config['canbus']['bustype'])

    mqttc = mqtt_client.Client(config['mqtt']['client_id'],
                               userdata=can_bus)
    mqttc.on_message = on_mqtt_message
    mqttc.reconnect_delay_set(1, 10)
    mqttc.will_set(config['mqtt']['will_topic'], '0xDEAD', 0, retain=True)
    mqttc.connect(host=config['mqtt']['host'],
                  port=int(config['mqtt']['port']),
                  keepalive=60)
    mqttc.loop_start()
    mqttc.subscribe('{}/#'.format(config['mqtt']['prefix']), 0)

    should_stop = False
    while not should_stop:
        try:
            can_msg = can_bus.recv(5)
            if can_msg:
                mqtt_msg = can2mqtt(can_msg)
                mqttc.publish(topic=mqtt_msg.topic,
                        payload=mqtt_msg.payload,
                        retain=False)
            mqttc.publish(topic=config['mqtt']['will_topic'],
                          payload='{:d}'.format(int(time())),
                          retain=True)
        except KeyboardInterrupt as e:
            print('exiting on keyboard request')
            should_stop = True
        except Exception as e:
            print(str(e))

    mqttc.disconnect()
