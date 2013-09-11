#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict

from cm_globals import MODES


class ExoType:
    """
    manage results on some type of exercices
    """
    def __init__(self):
        self.training = defaultdict(list)   # key is the level
        self.exercices = dict()             # key is the server exercice uid

    def currentLevel(self):
        for lvl in sorted(self.training.keys(), reverse=True):
            results = self.training[lvl]
            if len(results) >= 10 and sum(results[-10:]) >= 7:
                return lvl + 1
        return 0

    def addTrainingData(self, lvl, score):
        self.training[lvl].append(score)

    def addExerciceData(self, uid, data):
        """
        stocke les soumissions en cas de réseau indisponible,
        sinon, stocke les uis déjà réalisées.
        """
        self.exercices[uid] = data

    def __repr__(self):
        return 'ExoType(training=' + repr(self.training) + ', exercices=' + repr(self.exercices) + ')'


class UserData:
    """
    manage all the user's data
    """
    def __init__(self, nick, mail, password):
        self.nick = nick
        self.mail = mail
        self.pwd = password
        self.modes = OrderedDict([mode.name, ExoType()] for mode in MODES if mode.name != "Mode Libre")

    def get_mode(self, name):
        return self.modes[name]

    def __repr__(self):
        return '<UserData:\n' + '\n,'.join([self.nick, self.mail, self.pwd] + [repr(mode) for mode in self.modes.values()]) + '\n>'
