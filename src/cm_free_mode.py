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
from cm_controller import *


class FreeMode(QWidget):
    """
    Workspace widget for free-mode prototype.
    """
    
    closeRequested = Signal(QWidget)
    
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.graphical_group = GraphicalLispGroupWidget(self)
        self.terminal = TermWidget()
        self.close_btn = QPushButton(QIcon("../icons/cancel"), "Fermer")

        layout.addWidget(self.graphical_group)
        layout.addWidget(self.terminal)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

        self.terminal.setFocus()
        self.close_btn.clicked.connect(self.closeReq)

    def setController(self, controller):
        self.controller = controller
        self.terminal.read.connect(controller.receive)
        controller.send.connect(self.graphical_group.setExpr)

    def closeReq(self):
        self.closeRequested.emit(self)

######################################################
#                   constructors

def createFreeMode(userData):
    widget = FreeMode()
    controller = CmController(widget.terminal)
    widget.setController(controller)
    return widget
