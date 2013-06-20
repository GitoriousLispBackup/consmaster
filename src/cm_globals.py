import os.path
import pickle
from collections import namedtuple

from cm_workspace import createTextMode, createNormalToGraphicMode, createGraphicToNormalMode
from cm_free_mode import createFreeMode


Mode = namedtuple('Mode', ['name', 'src', 'constructor'])

MODES = [
    Mode("Mode Libre", '../data/mode-libre.html', createFreeMode),
    Mode("Standard <-> Dotted", None, createTextMode),
    Mode("Expr -> Graphique", None, createNormalToGraphicMode),
    Mode("Graphique -> Expr", None, createGraphicToNormalMode),
        ]


DATA_PATH = '../data/cm.dat'

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
