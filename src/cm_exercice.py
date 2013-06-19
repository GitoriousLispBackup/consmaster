import json

from cm_interm_repr import GraphExpr


class Encoder(json.JSONEncoder):
    """
    class encoder for serializable objects
    """
    def default(self, obj):
        if isinstance(obj, GraphExpr):
            dct = obj.__dict__
            dct['__GraphExpr__'] = True
            return dct
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def dec(dct):
    # print('entry', dct, dir(dct))
    if dct.pop('__GraphExpr__', None):
        return GraphExpr(**dct)
    return dct


def cmExerciceFactory(dct):
    typ = dct['typ']
    if typ == 'demo':
        return CmDemo(**dct)
    elif typ == '...':
        return None
    else:
        raise RuntimeError('unkown type: ' + typ)

class CmExerciceBase:
    """
    base class of exercices with
    JSON serialization support.
    """
    def __init__(self, typ):
        self.typ = typ

    def dump(self, filename):
        with open(filename, 'w', encoding='utf-8') as fp:
            return json.dump(self.__dict__, fp, cls=Encoder)

    @staticmethod
    def load(filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            dct = json.load(fp, object_hook=dec)
            return cmExerciceFactory(dct)


class CmDemo(CmExerciceBase):
    """
    demo class : not a real exercice
    """
    def __init__(self, **kwargs):
        super().__init__(typ=':demo')
        self.__dict__.update(kwargs)


######################################################

def load(filename):
    #~ filename, ok = QFileDialog.getOpenFileName(self, "Load file", '.', "ConsMaster Files (*.cm)")
    with open(filename, 'r', encoding='utf-8') as fp:
        return json.load(fp, object_hook=decoder)

def save(intermediate, filename):
    #~ filename, ok = QFileDialog.getSaveFileName(self, "Save file", '.', "ConsMaster Files (*.cm)")
    #~ if not filename.endswith('.cm'):
        #~ filename += '.cm'
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(intermediate, fp, cls=Encoder)

