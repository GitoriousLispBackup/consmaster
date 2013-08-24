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
    Mode("Mode Libre", '../data/mode-libre.html', None, createFreeMode),
    Mode("Standard <-> Dotted", '../data/norm-dot.html', '__NDN__', createTextMode),
    Mode("Expr -> Graphique", '../data/norm-graph.html', '__NG__', createNormalToGraphicMode),
    Mode("Graphique -> Expr", '../data/graph-norm.html', '__GN__', createGraphicToNormalMode),
        ]


DATA_DIR = '../data/'
CM_DATA = DATA_DIR + 'cm.dat'


def cm_load_data():
    fp = open(CM_DATA, 'rb')
    data = pickle.load(fp)
    fp.close()
    return data

def cm_save_data(data):
    fp = open(CM_DATA, 'wb')
    pickle.dump(data, fp)
    fp.close()

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)
if not os.path.exists(CM_DATA):
    cm_save_data([])

CM_BDD = PersistentDict(DATA_DIR + 'cm-bdd.dat')
