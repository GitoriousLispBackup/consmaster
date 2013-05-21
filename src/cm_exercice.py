import json

from cm_interm_repr import GraphExpr

class Encoder(json.JSONEncoder):
    """
    class encoder for serialisable exercices objects
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

class CmExercice:
    """
    :type:
    :data:
    :author:
    :level:
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def dump(self, filename):
        with open(filename, 'w', encoding='utf-8') as fp:
            return json.dump(self.__dict__, fp, cls=Encoder)

    @staticmethod
    def load(filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            d = json.load(fp, object_hook=dec)
            # 
            return CmExercice(**d)
