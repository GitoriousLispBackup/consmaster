#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

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

class CmTextController(QObject):
    enonce_changed = Signal(str)
    error = Signal(str)
    def __init__(self, typ='normal'):
        super().__init__()
        self.typ = typ
        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.interpreter.reset()
        self.enonce = exp_generator()
        method_inv = {'normal':'dotted_repr', 'dotted':'__repr__'}[self.typ]
        self.enonce_changed.emit(getattr(self.enonce, method_inv)())
        self.timer.start()

    @Slot(str)
    def receive(self, entry):
        # step 1 : check for empty data 
        if not entry.strip():
            self.error.emit('Vous devez entrer une expression valide.')
            return
        # step 2 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            self.error.emit("Erreur dans l'expression fournie.\nLe parseur a retourné " + repr(err))
            return
        # step 3 : check for conformity
        if not valid(entry, expr, self.typ):
            self.error.emit("L'expression n'est pas conforme au format attendu.\nVeuillez vérifier l'énoncé et le pretty-print.")
            return
        # step 4 : verify the entry
        self.verify(entry)            

    # TODO : add some help to user
    def verify(self, entry):
        method = {'dotted':'dotted_repr', 'normal':'__repr__'}[self.typ]
        excepted = getattr(self.enonce, method)()
        if entry == excepted:
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')


class CmNormalToGraphicController(QObject):
    enonce_changed = Signal(str)
    error = Signal(str)
    def __init__(self):
        super().__init__()

        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.interpreter.reset()
        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.enonce_changed.emit(repr(self.enonce))
        self.timer.start()

    @Slot(object)
    def receive(self, intermediate_repr):
        self.verify(intermediate_repr)

    # TODO : add some help to user
    def verify(self, intermediate):
        if intermediate == self.interm_enonce:
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')


class CmGraphicToNormalController(QObject):
    enonce_changed = Signal(object)
    error = Signal(str)
    def __init__(self):
        super().__init__()

        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.interpreter.reset()
        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.enonce_changed.emit(self.interm_enonce)
        self.timer.start()

    @Slot(str)
    def receive(self, entry):
        # step 1 : check for empty data 
        if not entry.strip():
            self.error.emit('Vous devez entrer une expression valide.')
            return
        # step 2 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            self.error.emit("Erreur dans l'expression fournie.\nLe parseur a retourné " + repr(err))
            return
        # step 3 : verify expr
        self.verify(expr)

    # TODO : add some help to user
    def verify(self, entry):
        if self.interm_enonce == GraphExpr.from_lsp_obj(entry):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')
