#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

from cm_interm_repr import GraphExpr


class Encoder(json.JSONEncoder):
    """
    class encoder for serializable objects
    """
    def default(self, obj):
        if isinstance(obj, GraphExpr):
            dct = obj.__dict__.copy()
            dct['__GraphExpr__'] = True
            return dct
        elif isinstance(obj, CmExerciceBase):
            dct = obj.__dict__.copy()
            dct['__ExoBase__'] = True
            return dct
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
  

def decoder(dct):
    if dct.pop('__GraphExpr__', None):
        return GraphExpr(**dct)
    elif dct.pop('__ExoBase__', None):
        typ = dct.pop('type')
        return CmExerciceBase.factory(typ, **dct)
    return dct



class CmExerciceBase:
    """
    base class of exercices with
    JSON serialization support.
    """
    @staticmethod
    def factory(typ, **kwargs):
        if typ == '__NDN__':
            return CmNDNExercice(**kwargs)
        elif typ == '__NG__':
            return CmNGExercice(**kwargs)
        elif typ == '__GN__':
            return CmGNExercice(**kwargs)
        else:
            raise RuntimeError('CmExerciceBase: unkown type: ' + typ)

    def __repr__(self):
        return '<Exercice: ' + repr(self.__dict__) + '>'


class CmNDNExercice(CmExerciceBase):
    """
    """
    def __init__(self, **kwargs):
        self.type = '__NDN__'
        self.__dict__.update(kwargs)

class CmNGExercice(CmExerciceBase):
    """
    """
    def __init__(self, **kwargs):
        self.type = '__NG__'
        self.__dict__.update(kwargs)

class CmGNExercice(CmExerciceBase):
    """
    """
    def __init__(self, **kwargs):
        self.type = '__GN__'
        self.__dict__.update(kwargs)

######################################################

def ex_load(filename):
    with open(filename, 'r', encoding='utf-8') as fp:
        return json.load(fp, object_hook=decoder)

def ex_save(obj, filename):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, cls=Encoder)

def ex_dumps(obj):
    return json.dumps(obj, cls=Encoder)

def ex_loads(s):
    return json.loads(s, object_hook=decoder)
