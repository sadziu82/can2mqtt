#!/usr/bin/env python


##
import paho.mqtt.client as mqttc


## monkeypatch comarison operator
mqttc.MQTTMessage.__eq__ = lambda self, other: self.topic == other.topic and self.payload == other.payload


##
class Mqtt(object):

    @staticmethod
    def message(topic, payload=None):
        msg = mqttc.MQTTMessage(topic=topic.encode('utf-8'))
        if payload is not None:
            msg.payload = payload
        return msg
