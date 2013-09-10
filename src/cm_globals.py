#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path
import pickle
from collections import namedtuple

from cm_workspace import createTextMode, createNormalToGraphicMode, createGraphicToNormalMode
from cm_free_mode import createFreeMode
from persistent_dict import PersistentDict


Mode = namedtuple('Mode', ['name', 'src', 'type', 'constructor'])

MODES = [
    # Mode("Mode Libre", '../data/mode-libre.html', None, createFreeMode),
    Mode("Standard <-> Dotted", '../data/norm-dot.html', '__NDN__', createTextMode),
    Mode("Expr -> Graphique", '../data/norm-graph.html', '__NG__', createNormalToGraphicMode),
    Mode("Graphique -> Expr", '../data/graph-norm.html', '__GN__', createGraphicToNormalMode),
        ]


DATA_DIR = '../data/'


if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

CM_DATA = PersistentDict(DATA_DIR + 'cm.dat')
CM_BDD = PersistentDict(DATA_DIR + 'cm-bdd.dat')

CM_DATA.setdefault('userlist', [])
