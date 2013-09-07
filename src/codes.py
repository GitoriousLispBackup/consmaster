#!/usr/bin/python3
# -*- coding: utf-8 -*-

## @package codes
# COURS   : EDF4REPA - IED - Paris 8
# PROJET  : consMaster2
# AUTEUR  : David Calmeille - 11299110@foad.iedparis8.net - L2
# FICHIER : codes.py
# CONTENU : codes
# VERSION : 0.2
# LICENCE : GNU


## Connexion au serveur
HOST = "localhost"
PORT = 9993


# Code Erreur Action
E_AUC = "Erreur: creatUser"
E_AUI = "Erreur: identUser"
E_AUD = "Erreur: delUser"
E_AUL = "Erreur: listtUser"
E_AUO = "Erreur: vous ne disposez pas des autorisations necessaires"
E_AUM = "Erreur: Cet utilisateur n'existe pas"


E_AEC = "Erreur: creatExo"
E_AEL = "Erreur: loadExo"
E_AED = "Erreur: delExo"

E_AJS = "Erreur: JSON format"
E_AUE = "Erreur: userExist"
E_AGA = "Erreur: pas de fonction de ce nom"
E_SRL = "Erreur: pas de variable action"

## Code Success Action
S_AUC = "creatUser"
S_AUI = "identUser"
S_AUD = "delUser"
S_AUL = "listUser"
S_AUM = "delMyUser"

S_AEC = "creatExo"
S_AEL = "loadExo"
S_AED = "delExo"



## Code Erreur Connexion

E_CJS = "Erreur: jsonCheck"
E_CSO = "Erreur: socketCreate"
E_CHO = "Erreur: Nom d\'hôte"
E_CCO = "Erreur: connection"
E_CSE = "Erreur: sendMessage"



## Compression
COMP = "Off"
#COMP = "On"



dicompress = {
  # action
       #   ' ':'',
   '"action":':'ac:',
     '"data":':'da:',
      '"nom":':'no:',
   '"prenom":':'pr:',
 '"password":':'pa:',
    '"droit":':'dr:',

 ## exos
    '"level":':'le:',
     '"type":':'ty:',
  '"__NDN__"':'"ndn"',
  '"__NG__"':'"ng"',
  '"__GN__"':'"gn"',
  '"__GraphExpr__"':'"ge"',
      '"root":':'rt:',
      '"graph":':'gr:',
      '"#atom"':'"at"',
      '"#cons"':'"cn"',
      '"layout":':'la:',
      '"lst":':'ls:',
      '"dotted"':'"do"',
      '"normal"':'"nr"',

 ## resultat
    '"status":':'st:',
    ':"error"':':er',
    ':"success"':':su',
    '"code":':'co:',
    '"description":':'de:',

 ## function action
':"creatUser"':':cu',
 ':"identUser"':':iu',
 ':"delUser"':':du',
 ':"listUser"':':lu',
 ':"creatExo"':':ce',
 ':"loadExo"':':lo',
 ':"delExo"':':dl'
}


