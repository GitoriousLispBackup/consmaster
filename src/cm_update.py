#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from cm_globals import CM_BDD
from cm_connexion import *
from cm_exercice import decoder


def update_bdd():
    raw_exos = get_exercices(); print(raw_exos)
    dct = {uid: json.loads(serialized, object_hook=decoder) for uid, serialized in raw_exos.items()}
    CM_BDD.update(dct); print(dct)
    CM_BDD.sync()
