import os.path
import pickle
from collections import namedtuple

from cm_workspace import createTextMode, createNormalToGraphicMode, createGraphicToNormalMode
from cm_free_mode import createFreeMode


Mode = namedtuple('Mode', ['name', 'src', 'location', 'constructor'])

MODES = [
    Mode("Mode Libre", '../data/mode-libre.html', None, createFreeMode),
    Mode("Standard <-> Dotted", '../data/norm-dot.html', "NormDot", createTextMode),
    Mode("Expr -> Graphique", '../data/norm-graph.html', "NormGraph", createNormalToGraphicMode),
    Mode("Graphique -> Expr", '../data/graph-norm.html', "GraphNorm", createGraphicToNormalMode),
        ]


DATA_PATH = '../data/cm.dat'
EXOS_DIR = '../save'

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
    if not os.path.exists(EXOS_DIR):
        os.mkdir(EXOS_DIR)
    for subdir in [mode.location for mode in MODES if mode.location is not None]:
        path = EXOS_DIR + '/' + subdir
        if not os.path.exists(path):
            os.mkdir(path)
