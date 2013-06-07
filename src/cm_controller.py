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
    send = Signal(GraphExpr)
    
    def __init__(self, term, widget):
        super().__init__()
        self.interpreter = Interpreter(out=term.out)
        
        term.read.connect(self.receive)
        self.send.connect(widget.insert_expr)

    @Slot(str)
    def receive(self, entry):
        retval = self.interpreter.eval(entry)
        gexpr = GraphExpr.from_lsp_obj(retval)
        self.send.emit(gexpr)

class CmTextController(QObject):
    enonce_changed = Signal(str)
    def __init__(self, typ='normal'):
        super().__init__()
        self.typ = typ
        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.enonce = exp_generator()
        self.enonce_changed.emit(self.get_enonce())
        self.timer.start()

    def get_enonce(self):
        method_inv = {'normal':'dotted_repr', 'dotted':'__repr__'}[self.typ]
        return 'expression à convertir :\n' + getattr(self.enonce, method_inv)()

    @Slot(str)
    def receive(self, entry):
        if self.validate(entry):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')

    # TODO : add some help to user
    def validate(self, entry):
        entry = re.sub(r' +', ' ', entry) # clean user entry
        method = {'dotted':'dotted_repr', 'normal':'__repr__'}[self.typ]
        excepted = getattr(self.enonce, method)()
        return entry == excepted


class CmNormalToGraphicController(QObject):
    enonce_changed = Signal(str)
    def __init__(self):
        super().__init__()

        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.enonce_changed.emit('expression à convertir :\n' + repr(self.enonce))
        self.timer.start()

    @Slot(object)
    def receive(self, intermediate_repr):
        if self.validate(intermediate_repr):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')

    # TODO : add some help to user
    def validate(self, intermediate):
        return intermediate == self.interm_enonce


class CmGraphicToNormalController(QObject):
    enonce_changed = Signal(object)
    def __init__(self):
        super().__init__()

        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

    def start(self):
        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.enonce_changed.emit(self.interm_enonce)
        self.timer.start()

    @Slot(str)
    def receive(self, entry):
        if self.validate(entry):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')

    # TODO : add some help to user
    def validate(self, entry):
        expr = self.interpreter.parse(entry)
        return self.interm_enonce == GraphExpr.from_lsp_obj(expr)
