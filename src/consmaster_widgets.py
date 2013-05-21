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
        self.createWidgets()

    def createWidgets(self) :
        grid = QGridLayout()

        #~ A glisp widget
        glispLabel = QLabel("Graph \nrepresentation")
        glispEntry = GlispWidget()
        glispButton = QPushButton("Validate")
        glispAdd = QPushButton("Add")
        glispRemove = QPushButton("Remove")
        glispCleanAll = QPushButton("CleanAll")
        glispFun = QPushButton("POWEEER")
        glispClean = QPushButton("Effacer")
        grid.addWidget(glispLabel, 0, 0, 1, 1)
        grid.addWidget(glispEntry, 0, 1)
        #~ vbox = QVBoxLayout()
        #~ vbox.addWidget(glispButton)
        #~ vbox.addWidget(glispClean)
        #~ vbox.addWidget(glispAdd)
        #~ vbox.addWidget(glispRemove)
        #~ vbox.addWidget(glispCleanAll)
        #~ vbox.addWidget(glispFun)
        tb = QToolBar()
        tb.setOrientation(Qt.Vertical)
        tb.setIconSize(QSize(30, 30))
        tb.addAction("Validate")
        tb.addAction("+ Cons", glispEntry.addCons)
        tb.addAction("+ Atom", glispEntry.addAtom)
        tb.addAction("Remove", glispEntry.removeItem)
        tb.addAction("Clear", glispEntry.removeAll)
        grid.addWidget(tb, 0, 5, 1, 1)
        #~ grid.addLayout(vbox, 0, 5, 1, 1)

        #~ Term-like widget
        termLabel = QLabel("Terminal")
        termEntry = TermWidget()
        termButton = QPushButton("Validate")
        grid.addWidget(termLabel, 1, 0, 1, 1)
        grid.addWidget(termEntry, 1, 1)
        grid.addWidget(termButton, 1, 5, 1, 1)
        termLabel.setBuddy(termEntry)

        termButton.clicked.connect(termEntry.out)

        self.setLayout(grid)
