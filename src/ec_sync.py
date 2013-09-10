#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple

from persistent_dict import PersistentDict


# keyed by name
ExoStorage = namedtuple('ExoStorage', ['id', 'type', 'level', 'serialized'])

