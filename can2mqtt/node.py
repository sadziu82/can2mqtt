#!/usr/bin/env python


##
_hc_node_shift = 8
_hc_node_mask  = 0x3FF << _hc_node_shift


##
class Node(object):

    @staticmethod
    def mqtt_decode(mqtt_node):
        return int(mqtt_node, 0x10)

    @staticmethod
    def mqtt2can(mqtt_node):
        return Node.can_encode(Node.mqtt_decode(mqtt_node))

    @staticmethod
    def can_decode(can_eid):
        node_id = (can_eid & _hc_node_mask) >> _hc_node_shift
        return node_id

    @staticmethod
    def can_encode(node_id):
        return ((node_id << _hc_node_shift) & _hc_node_mask)

    @staticmethod
    def can2mqtt(can_eid):
        return '{:X}'.format(Node.can_decode(can_eid))
