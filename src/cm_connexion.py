#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from server.connexion import Connexion
from cm_globals import CM_BDD, CM_DATA

#TODO : ajouter des messages d'erreur

def user_is_registered(user, pwd):
    dct = {'action': 'identUser', 'data': {'nickname': user, 'password': pwd}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, **CM_DATA['connexion_params'])
        response = json.loads(request.result)
        print(response)
        return response['status'] == 'success' and response['code'] == 'S_AUI'
    except:
        print('exception occured')
        return None

def create_user(user, pwd, email):
    dct = {'action': 'creatUser', 'data': {'nickname': user, 'password': pwd, 'email': email}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, **CM_DATA['connexion_params'])
        response = json.loads(request.result)
        print(response)
        return response['status'] == 'success' and response['code'] == 'S_AUC'
    except:
        print('exception occured')
        return None

def get_exercices():
    dct = {'action': 'loadExo', 'data': {}}
    data = json.dumps(dct)
    try:
        request = Connexion(data, **CM_DATA['connexion_params'])
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

def send_exercices(user_data):
    test = user_is_registered(user_data.nick, user_data.pwd)
    if test is None:
        print('unable to connect to network')
        return
    elif test is False:
        ok = create_user(user_data.nick, user_data.pwd, user_data.mail)
        if not ok:
            print('problem with user registration')
            return
            
    dct = {'action': 'creatSubm', 'nickname': user_data.nick, 'password': user_data.pwd}
    for exotype in user_data.modes.values():
        for uid, submission in exotype.exercices.items():
            if submission is None: continue
            dct['data'] = {"exo_id": uid, "soumission": submission}
            data = json.dumps(dct)
            try:
                request = Connexion(data, **CM_DATA['connexion_params'])
                response = json.loads(request.result)
                print(response)
                if response['status'] == 'success' and response['code'] == 'S_ASC':
                    exotype.exercices[uid] = None
                    #if CM_BDD[uid].once:
                        #exotype.exercices[uid] = None
                    #else:
                    #    del exotype.exercices[uid]
                else:
                    print(response['status'], response['code'])
            except:
                print('exception occured')
    # after all, resync user data
    CM_DATA.sync()
            

#def get_exercices_uid(uid):
    #dct = {'action': 'listExoId'}
    #data = json.dumps(dct)
    #try:
        #request = Connexion(data, **CM_DATA['connexion_params'])
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
