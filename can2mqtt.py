#!/usr/bin/env python
# -*- coding: utf-8 -*-


import can
import paho.mqtt.client as mqtt_client
import paho.mqtt.subscribe as mqtt_subscribe

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
        logger.error('mqtt message handling on topic {}: {}'.format(
                    mqtt_msg.topic, e))
    except Exception as e:
        print('*** {} {}'.format(str(mqtt_msg.topic), e))
        #pass


##
if __name__ == "__main__":
    ##
    logger.setLevel(logging.INFO)
    ##
    #bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
    can_bus = can.interface.Bus(channel='test', bustype='virtual')

    mqttc = mqtt_client.Client("can2mqtt")
    mqttc.on_message = on_mqtt_message
    mqttc.user_data_set(can_bus)
    mqttc.connect("192.168.105.2", 1883)
    mqttc.subscribe('#', 0)
    mqttc.loop_start()

    should_stop = False
    while not should_stop:
        try:
            can_msg = can_bus.recv(1)
            if can_msg:
                mqtt_msg = can2mqtt(can_msg)
                mqttc.publish(topic=mqtt_msg.topic,
                        payload=mqtt_msg.payload,
                        retain=False)
        except KeyboardInterrupt as e:
            print('exiting on keyboard request')
            should_stop = True
        except Exception as e:
            print(str(e))
        else:
            print('brak nowych danych')

    mqttc.unsubscribe('#')
