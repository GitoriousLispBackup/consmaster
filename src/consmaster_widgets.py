#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math

from cm_widgets.graphical_lisp import *
from cm_widgets.terminal import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)

class WidgetLayout(QWidget) :
    """ List of availables widgets"""

    def __init__(self, parent=None):
        super(WidgetLayout, self).__init__(parent)

        self.layout = QHBoxLayout()
        self.createWidgets()
        self.setLayout(self.layout)

    def createWidgets(self) :
        self.addGLispWidget()
        self.addTermWidget()

    def addGLispWidget(self) :
        #~ Add a glisp widget

        glispLabel = QLabel("Graph \nrepresentation")
        glispEntry = GlispWidget()
        glispAddCons = QPushButton("Add Cons")
        glispAddAtom = QPushButton("Add Atom")
        glispRemove = QPushButton("Remove")
        glispCleanAll = QPushButton("Clean All")

        hbox = QHBoxLayout()
        hbox.addWidget(glispLabel)
        hbox.addWidget(glispEntry)

        vbox = QVBoxLayout()
        vbox.addWidget(glispAddCons)
        vbox.addWidget(glispAddAtom)
        vbox.addWidget(glispRemove)
        vbox.addWidget(glispCleanAll)

        glispAddCons.clicked.connect(glispEntry.addCons)
        glispAddAtom.clicked.connect(glispEntry.addAtom)
        glispRemove.clicked.connect(glispEntry.removeItem)
        glispCleanAll.clicked.connect(glispEntry.removeAll)

        hbox.addLayout(vbox)

        self.layout.addLayout(hbox)

    def addTermWidget(self) :
        #~ Term-like widget
        termLabel = QLabel("Terminal")
        termEntry = TermWidget()
        termButton = QPushButton("Validate")

        hbox = QHBoxLayout()
        hbox.addWidget(termLabel)
        hbox.addWidget(termEntry)
        hbox.addWidget(termButton)

        termButton.clicked.connect(termEntry.out)

        self.layout.addLayout(hbox)
