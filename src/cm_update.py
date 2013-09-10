#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_globals import CM_BDD
from cm_connexion import *
from cm_exercice import ex_loads


def update_bdd():
    raw_exos = get_exercices(); print(raw_exos)
    # TODO: prevent if unable to connect to network
    if raw_exos.keys().isdisjoint(CM_BDD.keys()):
        QMessageBox.information(None, "Info", "De nouveaux exercices sont disponibles.")
        dct = {uid: ex_loads(serialized) for uid, serialized in raw_exos.items() if uid not in CM_BDD}
        CM_BDD.update(dct); # print(dct)
        CM_BDD.sync()
