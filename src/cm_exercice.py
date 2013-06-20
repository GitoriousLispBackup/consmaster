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
    # print('entry', dct, dir(dct))
    if dct.pop('__GraphExpr__', None):
        return GraphExpr(**dct)
    elif dct.pop('__ExoBase__', None):
        typ = dct.pop('type')
        if typ == '__NDN__':
            return CmNDNExercice(**dct)
        elif typ == '__NG__':
            return CmNGExercice(**dct)
        elif typ == '__GN__':
            return CmGNExercice(**dct)
        else:
            raise RuntimeError('unkown type: ' + typ)
    return dct



class CmExerciceBase:
    """
    base class of exercices with
    JSON serialization support.
    """
    pass
#    def dump(self, filename):
#        with open(filename, 'w', encoding='utf-8') as fp:
#            return json.dump(self.__dict__, fp, cls=Encoder)

#    @staticmethod
#    def load(filename):
#        with open(filename, 'r', encoding='utf-8') as fp:
#            dct = json.load(fp, object_hook=dec)
#            return cmExerciceFactory(dct)


class CmNDNExercice(CmExerciceBase):
    """
    """
    def __init__(self, level, lst):
        self.type = '__NDN__'
        self.level = level
        self.lst = lst
        
class CmNGExercice(CmExerciceBase):
    """
    """
    def __init__(self, level, lst):
        self.type = '__NG__'
        self.level = level
        self.lst = lst
        
class CmGNExercice(CmExerciceBase):
    """
    """
    def __init__(self, level, lst):
        self.type = '__GN__'
        self.level = level
        self.lst = lst


######################################################

def ex_load(filename):
    print('load', filename)
    #~ filename, ok = QFileDialog.getOpenFileName(self, "Load file", '.', "ConsMaster Files (*.cm)")
    with open(filename, 'r', encoding='utf-8') as fp:
        return json.load(fp, object_hook=decoder)

def ex_save(obj, filename):
    #~ filename, ok = QFileDialog.getSaveFileName(self, "Save file", '.', "ConsMaster Files (*.cm)")
    #~ if not filename.endswith('.cm'):
        #~ filename += '.cm'
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, cls=Encoder)

