#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from server.connexion import Connexion

#TODO: utiliser des paramètres
HOST, PORT = 'eliacheff.dyndns.org', 9993
# HOST, PORT = 'localhost', 9993

#TODO : ajouter des messages d'erreur

def user_is_registered(user, pwd):
    dct = {'action': 'identUser', 'data': {'nickname': user, 'password': pwd}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, host=HOST, port=PORT)
        response = json.loads(request.result)
        print(response)
        return response['status'] == 'success' and response['code'] == 'S_AUI'
    except:
        print('exception occured')
        return False

def create_user(user, pwd, email):
    dct = {'action': 'creatUser', 'data': {'nickname': user, 'password': pwd, 'email': email}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, host=HOST, port=PORT)
        response = json.loads(request.result)
        print(response)
        return response['status'] == 'success' and response['code'] == 'S_AUC'
    except:
        print('exception occured')
        return False

def get_exercices():
    dct = {'action': 'loadExo', 'data': {}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, host=HOST, port=PORT)
        response = json.loads(request.result)
        #print(response)
        if response['status'] == 'success' and response['code'] == 'S_AEL':
            return {e['id']: e['raw'] for e in response['data']}
        else:
            print(response['status'], response['code'])
            return None
    except Exception as err:
        print('exception occured', repr(err))
        return None

def send_exercices(userData):
    nick, password = userData.nick, userData.pwd
    
#def get_exercices_uid(uid):
    #dct = {'action': 'listExoId'}
    #data = json.dumps(dct)
    #try:
        #request = Connexion(data, host=HOST, port=PORT)
        #response = json.loads(request.result)
        ##print(response)
        #if response['status'] == 'success' and response['code'] == 'S_AEL':
            #return set(response['data'])
        #else:
            #print(response['status'], response['code'])
            #return None
    #except:
        #print('exception occured')
        #return None
