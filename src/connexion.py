#!/usr/bin/python3
# -*- coding: utf-8 -*-

## @package connexion
# COURS   : EDF4REPA - IED - Paris 8
# PROJET  : consMaster2
# AUTEUR  : David Calmeille - 11299110@foad.iedparis8.net - L2
# FICHIER : connexion.py
# CONTENU : Class Connexion (client)
# USAGE   : new_a = Connexion(data, comp, PORT, HOST)
# VERSION : 0.2
# LICENCE : GNU

import socket
import time
import json
import sys

from codes import *
from compress import *



class Connexion:

    def __init__(self, mess='', comp=COMP, port=PORT, host=HOST):
        ## initilisation des variables
        self.mess = mess
        self.port = port
        self.host = host
        self.comp = comp

        self.jsonCheck()


    def jsonCheck(self):
        ## vérifie si le message est au format JSON
        try:
            json.loads(self.mess)
        except ValueError:
            self.erreur = ("Erreur: les données ne sont pas au format JSON")
            self.result = '{"status":"error","code":"E_CJS","description":"Erreur: les données ne sont pas au format JSON."}'
            return 1

        if (self.comp == "On"):
            #print("Compress Me")
            new_c = compression(self.mess)
            new_c.dataCompression()
            #print("compression 1:", new_c.comp)
            self. mess = new_c.comp
            self.socketCreate()
        else:
            self.socketCreate()


    def socketCreate(self):
        ## création d'un socket TCP/IP V4 avec une communication par flot de données
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ## print ('Socket crée')
        except socket.error:
            self.erreur = ('Erreur: Impossible de créer un socket')
            self.result = '{"status":"error","code":"E_CSO","description":"Erreur: Impossible de créer un socket."}'
            return 1
        self.connection()


    def connection(self):
        try:
            ## Traduit le host name en adresse ip
            self.remote_ip = socket.gethostbyname( self.host )
        except socket.gaierror:
            self.erreur = 'Erreur: Nom de l\'hôte ne peut être résolu.'
            self.result = '{"status":"error","code":"E_CHO","description":"Erreur: Nom de l\'hôte ne peut être résolu."}'
            return 1

        try:
            ## établit une connexion avec le serveur.
            self.s.connect((self.remote_ip , self.port))
            ## print ('Socket Connecté à ' + self.host + ' sur ip: ' + self.remote_ip)
        except socket.error as e:
            self.erreur = "Erreur:Impossible de se connecter à " + self.host + " sur le port: " + str(self.port)
            self.result = '{"status":"error","code":"E_CCO","description":"Erreur:Impossible de se connecter à ' + self.host + ' sur le port: ' + str(self.port) + '"}'
            return 1

        self.sendMessage()


    def sendMessage(self):
        try :
            ## Envoie les données au serveur
            self.s.sendall(bytes(self.mess, "utf-8"))
        except socket.error:
            self.erreur = 'Erreur: Impossible d\'envoyer le message'
            self.result = '{"status":"error","code":"E_CSE","description":"Erreur: Impossible d\'envoiyer le message"}'
            return 1


        ## print ('Message envoyer avec succès')


        def reception(leSocket,timeOut=1):
            ## faire un socket non bloquant
            leSocket.setblocking(0)

            allData=[];
            data='';

            ## debut du temps
            debut=time.time()
            while 1:
                ## si il y a des données, break après le timeout
                if allData and time.time()-debut > timeOut:
                    break

                ## si il n'y a pas de données, attendre un peu plus longtemps.
                elif time.time()-debut > timeOut*2:
                    break

                ## réception
                try:
                    data = str(leSocket.recv(1024), "utf-8")
                    if data:
                        allData.append(data)
                        ## modifier le temps de debut
                        debut=time.time()
                    else:
                        ## dormir un certain temps pour indiquer un écart
                        time.sleep(0.1)
                except:
                    pass

            ## rejoindre toutes les parties de la chaîne
            return ''.join(allData)

        ## obtenir la réponse
        resul = reception(self.s)
        new_d = decompression(resul)
        myrecomp = new_d.dataDecompression()

        if (new_d.recomp == "On"):
            self.result =  myrecomp
        else:
            self.result = resul
        ## ferme le socket
        self.s.close()




