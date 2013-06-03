#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

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
        self.send.emit(retval)

class CmTextController(QObject):
    send = Signal(GraphExpr)
    
    def __init__(self, label, lineEdit):
        super().__init__()
        self.interpreter = Interpreter(out=print)

        lineEdit.send.connect(self.receive)

        self.enonce = exp_generator()
        label.setText('expression à convertir :\n' + repr(self.enonce))
        #self.send.connect(widget.insert_expr)

    @Slot(str)
    def receive(self, entry):
        retval = self.interpreter.eval(entry)
        print(retval) # receive GraphExpr
        # self.send.emit(retval)
