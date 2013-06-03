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
        label.setText('expression à convertir :\n' + repr(self.enonce))
        self.timer.start()

    @Slot(str)
    def receive(self, entry):
        if self.validate(entry):
            print('OK', self.timer.elapsed(), 'ms')
        else:
            print('KO', self.timer.elapsed(), 'ms')

    # TODO : add some help to user
    def validate(self, entry):
        entry = re.sub(r' +', '', entry) # clean entry
        method = {'dotted':'dotted_repr', 'normal':'__repr__'}[self.typ]
        excepted = getattr(self.enonce, method)()
        print(entry, excepted)
        return entry == excepted
