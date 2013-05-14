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
        glispLabel = QLabel("Graph representation")
        glispEntry = GlispWidget()
        glispButton = QPushButton("Validate")
        glispClean = QPushButton("Effacer")
        grid.addWidget(glispLabel, 0, 0, 1, 1)
        grid.addWidget(glispEntry, 0, 1)
        vbox = QVBoxLayout()
        vbox.addWidget(glispButton)
        vbox.addWidget(glispClean)
        grid.addLayout(vbox, 0, 5, 1, 1)

        #~ Term-like widget
        termLabel = QLabel("Terminal")
        termEntry = TermWidget()
        termButton = QPushButton("Validate")
        grid.addWidget(termLabel, 1, 0, 1, 1)
        grid.addWidget(termEntry, 1, 1)
        grid.addWidget(termButton, 1, 5, 1, 1)
        termLabel.setBuddy(termEntry)

        termButton.clicked.connect(termEntry.printSelf)

        self.setLayout(grid)
