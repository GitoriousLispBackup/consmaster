#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import random

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from pylisp import *
import pylisp.lisp_errors as lisp_errors
from lisp_errors import LispError, LispParseError

from cm_lisp_graphic import *
from cm_terminal import *
from cm_interpreter import Interpreter, GraphExpr
from cm_expr_generator import exp_generator


class CmController(QObject):
    send = Signal(object)

    def __init__(self, term):
        super().__init__()
        self.interpreter = Interpreter(out=term.out)

    @Slot(str)
    def receive(self, entry):
        retval = self.interpreter.eval(entry)
        if retval is not None:
            gexpr = GraphExpr.from_lsp_obj(retval)
            self.send.emit(gexpr)

############################################################
#               controllers for exercices

def valid(entry, expr, fmt='normal', strict=True):
    if not strict:
        entry = re.sub(r' +', ' ', entry)   # clean user entry
    method = {'dotted':'dotted_repr', 'normal':'__repr__'}[fmt]
    excepted = getattr(expr, method)()
    return entry == excepted

# TODO : deal with level
def simple_gen(level=None):
    while True:
        yield exp_generator()


class CmBasicController(QObject):
    enonceChanged = Signal(object)
    error = Signal(str)
    ok = Signal()
    
    def __init__(self):
        super().__init__()
        self.interpreter = Interpreter(out=print)
    

class TrainingMixin:
    def __init__(self, userData):
        self.userData = userData
        self.currentLevel = userData.current_level() if userData else None
        self.enonceIter = simple_gen(self.currentLevel if self.currentLevel else 0)
        
    def next(self):
        self.enonce = next(self.enonceIter)
        return self.enonce
        
    @Slot(object)
    def receive(self, entry):
        if self.validate(entry):
            self.verify(entry)
            
    def updateData(self, score):
        if self.userData:
            self.userData.training[self.currentLevel].append(score)
            lvl = self.userData.current_level()
            if lvl > self.currentLevel:
                # TODO : announce that
                print('upgrade level to', lvl)
                self.currentLevel = lvl
                self.enonceIter = simple_gen(self.currentLevel)
        
    def verify(self, entry):
        ok = self.test(entry)
        self.updateData(1 if ok else 0)
        if ok:                
            self.ok.emit()
        else:
            # TODO : add help to user
            print('KO')


class CmNormalDottedConvTController(CmBasicController, TrainingMixin):
    methods = {'dotted':'dotted_repr', 'normal':'__repr__'}
    inv_methods = {'normal':'dotted_repr', 'dotted':'__repr__'}

    def __init__(self, userData=None):
        CmBasicController.__init__(self)
        TrainingMixin.__init__(self, userData)
    
    def next(self):
        super().next()
        self.typ = random.choice(list(self.methods.keys()))
        method_inv = self.inv_methods[self.typ]
        self.enonceChanged.emit('<i>[' + self.typ + ']</i><br>' + getattr(self.enonce, method_inv)())
    
    def validate(self, entry):
        # step 1 : check for empty data 
        if not entry.strip():
            self.error.emit('Vous devez entrer une expression valide.')
            return False
        # step 2 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            self.error.emit("Erreur dans l'expression fournie.\nLe parseur a retourné " + repr(err))
            return False
        # step 3 : check for conformity
        if not valid(entry, expr, self.typ):
            self.error.emit("L'expression n'est pas conforme au format attendu.\nVeuillez vérifier l'énoncé et le pretty-print.")
            return False
        return True
        
    def test(self, entry):
        method = self.methods[self.typ]
        excepted = getattr(self.enonce, method)()
        return entry == excepted


class CmNormalToGraphicTController(CmBasicController, TrainingMixin):
    def __init__(self, userData=None):
        CmBasicController.__init__(self)
        TrainingMixin.__init__(self, userData)

    def next(self):
        super().next()
        self.enonceChanged.emit(repr(self.enonce))

    def validate(self, entry):
        # some verifications occurs at GUI level
        if entry is None:
            return False
        return True
        
    def test(self, entry):
        return entry == GraphExpr.from_lsp_obj(self.enonce)

        
class CmGraphicToNormalTController(CmBasicController, TrainingMixin):
    def __init__(self, userData=None):
        CmBasicController.__init__(self)
        TrainingMixin.__init__(self, userData)

    def next(self):
        super().next()
        self.enonce_intermediate = GraphExpr.from_lsp_obj(self.enonce)
        self.enonceChanged.emit(self.enonce_intermediate)

    def validate(self, entry):
        # step 1 : check for empty data 
        if not entry.strip():
            self.error.emit('Vous devez entrer une expression valide.')
            return False
        # step 2 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            self.error.emit("Erreur dans l'expression fournie.\nLe parseur a retourné " + repr(err))
            return False
        return True

    def test(self, entry):
        return GraphExpr.from_lsp_obj(entry) == self.enonce_intermediate
