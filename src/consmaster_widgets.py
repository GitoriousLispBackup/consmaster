#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math
from collections import OrderedDict

from cm_lisp_graphic import *
from cm_terminal import *
from cm_controller import CmController
from consmaster_widget_rc import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)



class MainMenu(QWidget) :
    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()

        self.mainwindow = mainwindow
        
        self.layout = QHBoxLayout()

        self.basicMenu()

        self.setLayout(self.layout)

    #~ Basic and static menu
    #~ TODO: should link to the correct text
    def basicMenu(self) :
        scrollContent = QWidget()
        #~ self.resize(50,100)

        btn_names = ["Mode Libre", "Entrainement", "Représentation\ndoublets", "Représentation\na points", "Représentation\ngraphique"]
        self.buttons_dct = OrderedDict([(name, QPushButton(name, scrollContent)) for name in btn_names])

        self.buttons_dct["Mode Libre"].clicked.connect(self.createFreeMode)

        #~ Layout in the scroll area
        vb = QVBoxLayout()

        for button in self.buttons_dct.values():
            button.setCheckable(True)
            button.setFixedSize(120,120)
            vb.addWidget(button)

        scrollContent.setLayout(vb)

        #~ Group buttonns to make them exclusive
        group = QButtonGroup(scrollContent)
        for button in self.buttons_dct.values():
            group.addButton(button)
        group.setExclusive(True)

        scroller = QScrollArea()
        scroller.setWidget(scrollContent)
        scroller.setFixedWidth(155)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.layout.addWidget(scroller)

        #~ The text/hints display widget + his button
        vb = QVBoxLayout()
        displayText = QTextEdit()
        displayText.setReadOnly(True)
        displayText.setText(modeLibre)
        launchButton = QPushButton("Démarrer", self)
        launchButton.setFixedHeight(50)

        vb.addWidget(displayText)
        vb.addWidget(launchButton)
        self.layout.addLayout(vb)

    def closeWidget(self, widget):
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.closeAction.setEnabled(False)
        del widget.controller  # why I must to manually do that ?

    def createFreeMode(self):
        widget = QWidget()

        layout = QVBoxLayout()

        graphical_group = GraphicalLispGroupWidget(widget)
        layout.addWidget(graphical_group)

        terminal_group = TerminalGroupWidget()
        layout.addWidget(terminal_group)

        widget.setLayout(layout)

        widget.controller = CmController(terminal_group.term, graphical_group.glisp_widget)

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

        self.mainwindow.closeAction.triggered.connect(lambda: self.closeWidget(widget))
        self.mainwindow.closeAction.setEnabled(True)

        terminal_group.term.setFocus()
        

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
