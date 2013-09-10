#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os.path
from collections import namedtuple

from persistent_dict import PersistentDict



Mode = namedtuple('Mode', ['name', 'src', 'type'])

MODES = [
    # Mode("Mode Libre", '../data/mode-libre.html', None),
    Mode("Standard <-> Dotted", '../data/norm-dot.html', '__NDN__'),
    Mode("Expr -> Graphique", '../data/norm-graph.html', '__NG__'),
    Mode("Graphique -> Expr", '../data/graph-norm.html', '__GN__'),
        ]


DATA_DIR = '../data/'

if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

CM_DATA = PersistentDict(DATA_DIR + 'cm.dat')
CM_BDD  = PersistentDict(DATA_DIR + 'cm-bdd.dat')

CM_DATA.setdefault('userlist', [])
