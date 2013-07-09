#!/usr/bin/python3
# -*- coding: utf-8 -


class ServerInteraction(object):
    '''
    Class used to sync locals exercices with a remote server
    '''

    def __init__(self):
        self.login = ""
        self.password = ""
        self.remote = ""
        self.dest = ""

    def connectToServer(self):
        """ Get a connection """
        pass

    def sendToServer(self):
        """ Send files to server """
        pass

    def getFromServer(self):
        """ Download new files """
        pass

    def sync(self):
        """ Automatic synchronization """
        pass
