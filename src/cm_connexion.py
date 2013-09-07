#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from connexion import Connexion


def ensure_user_is_registered(user, pwd):
    dct = {'action': 'identUser', 'data': {'nickname': user, 'password': pwd}}
    data = json.dumps(dct)
    try:
        request = Connexion(data)
        response = json.loads(request.result)
        print(response)
        return response['status'] == 'success' and response['code'] == 'S_AUI' and response['data']
    except:
        print('exception occured')
        return False

def create_user(user, pwd, email):
    dct = {'action': 'creatUser', 'data': {'nickname': user, 'password': pwd, 'email': email}}
    data = json.dumps(dct)
    try:
        request = Connexion(data)
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
        request = Connexion(data)
        response = json.loads(request.result)
        #print(response)
        if response['status'] == 'success' and response['code'] == 'S_AEL':
            return {e['id']: e['raw'] for e in response['data']}
        else:
            print(response['status'], response['code'])
            return {}
    except Exception as err:
        print('exception occured', repr(err))
        return {}

def get_exercice_by_uid(uid):
    dct = {'action': 'loadExo', 'data': {'id': uid}}
    data = json.dumps(dct)
    try:
        request = Connexion(data)
        response = json.loads(request.result)
        #print(response)
        if response['status'] == 'success' and response['code'] == 'S_AEL' and response['data']:
            return [e['raw'] for e in response['data']][0]
        else:
            print(response['status'], response['code'])
            return None
    except:
        print('exception occured')
        return None

