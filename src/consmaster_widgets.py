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
        super().__init__(parent)

        self.layout = QVBoxLayout()

        graphical_lisp = GraphicalLispGroupWidget(self)
        self.layout.addWidget(graphical_lisp)

        terminal = TerminalGroupWidget()
        self.layout.addWidget(terminal)

        self.setLayout(self.layout)


class MainMenu(QWidget) :
    """ Main menu creation/gestion
    List of availables widgets"""

    def __init__(self, parent=None):
        super(Client, self).__init__(parent)

        self.layout = QVBoxLayout()

        graphical_lisp = GraphicalLispGroupWidget(self)
        self.layout.addWidget(graphical_lisp)

        terminal = TerminalGroupWidget()
        self.layout.addWidget(terminal)

        self.setLayout(self.layout)


class TerminalControl(QWidget) :
    """ Controller for TermWidget """
    def __init__(self, parent=None):
        super().__init__(parent)


class GLispControl(QWidget) :
    """ Controller for GlispWidget """
    def __init__(self, parent=None):
        super().__init__(parent)


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
