#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict
from cm_globals import MODES
from cm_connexion import user_is_registered, create_user

class ExoType:
    """
    manage results on some type of exercices
    """
    def __init__(self):
        self.training = defaultdict(list)   # key is the level
        self.exercices = defaultdict(dict)  # idem

    def currentLevel(self):
        for lvl in sorted(self.training.keys(), reverse=True):
            results = self.training[lvl]
            if len(results) >= 10 and sum(results[-10:]) >= 7:
                return lvl + 1
        return 0

    def addTrainingData(self, lvl, score):
        self.training[lvl].append(score)

    def addExerciceData(self, lvl, uid, score):
        self.exercices[lvl][uid] = score

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
        self._registered = False

    def get_mode(self, name):
        return self.modes[name]

    def __repr__(self):
        return '<UserData:\n' + '\n,'.join([self.nick, self.mail, self.pwd] + [repr(mode) for mode in self.modes.values()]) + '\n>'

    def register(self):
        if self._registered:
            return
        elif user_is_registered(self.nick, self.pwd):
            self._registered = True
            print('user already registered')
        else:
            print('register', self.nick)
            self._registered = create_user(self.nick, self.pwd, self.mail)

    def getRegistered(self):
        return self._registered

    registered = property(fget=getRegistered)
