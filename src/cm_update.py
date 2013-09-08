#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from cm_globals import CM_BDD
from cm_connexion import *
from cm_exercice import decoder


def update_bdd():
    raw_exos = get_exercices(); # print(raw_exos)
    # TODO: prevent if unable to connect to network
    if raw_exos.keys() > CM_BDD.keys():
        QMessageBox.information(self, "Info", "De nouveaux exercices sont disponibles.")
        dct = {uid: json.loads(serialized, object_hook=decoder) for uid, serialized in raw_exos.items() if uid not in CM_BDD}
        CM_BDD.update(dct); # print(dct)
        CM_BDD.sync()
