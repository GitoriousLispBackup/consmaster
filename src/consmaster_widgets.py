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
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

class WidgetsLayout(QWidget) :
    """ List of availables widgets"""

    def __init__(self, parent=None):
        super(WidgetsLayout, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.createWidgets()
        self.setLayout(self.layout)

    def createWidgets(self) :
        self.addGLispWidget()
        self.addTermWidget()

    def addGLispWidget(self) :
        #~ Add a glisp widget

        glispLabel = QLabel("Graph \nrepresentation")
        glispLabel.setFixedWidth(110)
        glispEntry = GlispWidget()
        glispAddCons = QPushButton("Add Cons")
        glispAddAtom = QPushButton("Add Atom")
        glispRemove = QPushButton("Remove")
        glispCleanAll = QPushButton("Clean All")

        #~ Main container
        hbox = QHBoxLayout()
        hbox.addWidget(glispLabel)
        hbox.addWidget(glispEntry)

        #~ Control buttons container
        vbox = QVBoxLayout()
        vbox.addWidget(glispAddCons)
        vbox.addWidget(glispAddAtom)
        vbox.addWidget(glispRemove)
        vbox.addWidget(glispCleanAll)

        #~ Actions
        glispAddCons.clicked.connect(glispEntry.addCons)
        glispAddAtom.clicked.connect(glispEntry.addAtom)
        glispRemove.clicked.connect(glispEntry.removeItem)
        glispCleanAll.clicked.connect(glispEntry.removeAll)

        hbox.addLayout(vbox)

        self.layout.addLayout(hbox)

    def addTermWidget(self) :
        #~ Term-like widget
        termLabel = QLabel("Terminal")
        termLabel.setFixedWidth(110)
        termEntry = TermWidget()
        termButton = QPushButton("Validate")

        #~ Main container
        hbox = QHBoxLayout()
        hbox.addWidget(termLabel)
        hbox.addWidget(termEntry)
        hbox.addWidget(termButton)

        termButton.clicked.connect(termEntry.out)

        self.layout.addLayout(hbox)

class MainMenu(QWidget) :
    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        self.basicMenu()

        self.setLayout(self.layout)

    #~ Basic and static menu
    def basicMenu(self) :
        scrollContent = QWidget()
        #~ self.resize(50,100)

        #~ Should be automated
        b1 = QPushButton("jhgvkjfv1", scrollContent)
        b2 = QPushButton("jhgvkjfv2", scrollContent)
        b3 = QPushButton("jhgvv2", scrollContent)
        b4 = QPushButton("jhgvkjfv4", scrollContent)
        b5 = QPushButton("jhgvkjfv5", scrollContent)

        b1.setCheckable(True)
        b1.setChecked(True)
        b1.setFixedSize(120,120)
        b2.setCheckable(True)
        b2.setFixedSize(120,120)
        b3.setCheckable(True)
        b3.setFixedSize(120,120)
        b4.setCheckable(True)
        b4.setFixedSize(120,120)
        b5.setCheckable(True)
        b5.setFixedSize(120,120)

        #~ Layout in the scroll area
        vb = QVBoxLayout()
        vb.addWidget(b1)
        vb.addWidget(b2)
        vb.addWidget(b3)
        vb.addWidget(b4)
        vb.addWidget(b5)
        scrollContent.setLayout(vb)

        #~ Group buttonns to make them exclusive
        group = QButtonGroup(scrollContent)
        group.addButton(b1)
        group.addButton(b2)
        group.addButton(b3)
        group.addButton(b4)
        group.addButton(b5)

        group.setExclusive(True)

        scroller = QScrollArea()
        scroller.setWidget(scrollContent)
        scroller.setFixedWidth(150)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.layout.addWidget(scroller)

        #~ The text/hints display widget + his button
        vb = QVBoxLayout()
        displayText = QTextBrowser()
        launchButton = QPushButton("Démarrer", self)
        launchButton.setFixedHeight(50)

        vb.addWidget(displayText)
        vb.addWidget(launchButton)
        self.layout.addLayout(vb)

    #~ TODO: Final dynamic Menu
    def createMenu(self) :
        #~ Basic modules
        #~ Should implement custom modules creation via a
        #~ dedicated class

        scroll = QScrollArea()

        vbox = QVBoxLayout()

    #~ Start of a custom mod creation program, should be in a dedicated
    #~ file
    def buttonMod(self, text, icon=None, file=None) :
        """ Button creator for custom mods

        Args :
            text : A display text

            Optionnal :
            icon : An icon can be added
            file : The file containing summary text and exercices details,
                    etc... and the exercices themself
        """

        button = QPushButton()
