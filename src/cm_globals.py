DATA_PATH = '../data/cm.dat'
# CURRENT_USER = None


ModeName = [
    "Standard <-> Dotted", 
    "Expr -> Graphique",
    "Graphique -> Expr"
    ]

NDN_CONV_MODE = 0   # normal <-> dotted
NG_CONV_MODE = 1    # normal -> graphic
GN_CONV_MODE = 2    # graphic -> normal

import os.path
import pickle
from cm_monitor import *

def cm_load_data():
    fp = open(DATA_PATH, 'rb')
    data = pickle.load(fp)
    fp.close()
    return data

def cm_save_data(data):
    fp = open(DATA_PATH, 'wb')
    pickle.dump(data, fp)
    fp.close()

def cm_init():
    if not os.path.exists(DATA_PATH):
        cm_save_data([])
