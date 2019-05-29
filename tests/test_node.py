#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from can2mqtt.node import Node


## fixtures
@pytest.fixture()
def hc_nodes():
   return [
        ('12', 0x1200),
        ('69', 0x6900),
    ]


## tests
def test_node_mqtt2can(hc_nodes):
    for mqtt, can in hc_nodes:
        assert Node.mqtt2can(mqtt) == can

def test_node_can2mqtt(hc_nodes):
    for mqtt, can in hc_nodes:
        assert Node.can2mqtt(can) == mqtt
