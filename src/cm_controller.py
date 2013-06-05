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
    def __init__(self, label, lineEdit, typ='normal'):
        super().__init__()
        self.typ = typ
        self.enonce = exp_generator()
        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

        lineEdit.send.connect(self.receive)
        method_inv = {'normal':'dotted_repr', 'dotted':'__repr__'}[typ]
        label.setText('expression à convertir :\n' + getattr(self.enonce, method_inv)())
        self.timer.start()

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
    def __init__(self, label, glisp, validateBtn):
        super().__init__()
        self.glisp = glisp

        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

        label.setText('expression à convertir :\n' + repr(self.enonce))

        validateBtn.clicked.connect(self.receive)
        self.timer.start()

    def receive(self):
        intermediate_repr = self.glisp.glisp_widget.get_expr()
        if self.validate(intermediate_repr):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')

    # TODO : add some help to user
    def validate(self, intermediate):
        return intermediate == self.interm_enonce


class CmGraphicToNormalController(QObject):    
    def __init__(self, glisp, lineEdit):
        super().__init__()

        self.enonce = exp_generator()
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        self.interpreter = Interpreter(out=print)
        self.timer = QElapsedTimer()

        glisp.insert_expr(self.interm_enonce)
        glisp.setInteractive(False)

        lineEdit.send.connect(self.receive)
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
