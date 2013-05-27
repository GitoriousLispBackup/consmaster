#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_widgets.graphical_lisp import *
from cm_widgets.terminal import *
from cm_interpreter import Interpreter, GraphExpr

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

