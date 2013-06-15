#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pickle
import textwrap

from cm_globals import *
from cm_free_mode import *
from cm_workspace import *
from cm_monitor import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class ButtonMenu(QPushButton):
    def __init__(self, textSrc, func, name, parent):
        super().__init__(name, parent)
        self.description = open(textSrc, 'r', encoding='utf-8').read() if textSrc else 'information manquante sur ce mode'
        self.constructor = func


class MainMenu(QWidget) :
    Modes = [
        ("Mode Libre", '../data/mode-libre.html', createFreeMode),
        (ModeName[NDN_CONV_MODE], None, createTextMode),
        (ModeName[NG_CONV_MODE], None, createNormalToGraphicMode),
        (ModeName[GN_CONV_MODE], None, createGraphicToNormalMode),
            ]

    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.basicMenu()

    #~ Basic and static menu
    #~ TODO: should link to the correct text
    def basicMenu(self):
        self.layout = QHBoxLayout()

        scrollContent = QWidget()
        #~ self.resize(50,100)

        #~ Layout in the scroll area
        vb = QVBoxLayout()
        self.buttons_group = QButtonGroup()
        self.buttons_group.setExclusive(True)

        for name, src, func in MainMenu.Modes:
            name = '\n'.join(textwrap.wrap(name, 10))
            btn = ButtonMenu(src, func, name, scrollContent)
            btn.setCheckable(True)
            btn.setFixedSize(120,120)
            vb.addWidget(btn)
            self.buttons_group.addButton(btn)
        self.buttons_group.buttonClicked.connect(self.displayMode)

        #~ btns = self.buttons_group.buttons()
        #~ if btns: btns[0].click()

        scrollContent.setLayout(vb)

        scroller = QScrollArea()
        scroller.setWidget(scrollContent)
        scroller.setFixedWidth(155)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.layout.addWidget(scroller)

        #~ The text/hints display widget + his button
        vb = QVBoxLayout()
        self.displayText = QTextEdit()
        self.displayText.setReadOnly(True)

        launchButton = QPushButton("S'entrainer", self)
        launchButton.setFixedHeight(50)
        launchButton.clicked.connect(self.startSelectedMode)

        vb.addWidget(self.displayText)
        vb.addWidget(launchButton)
        self.layout.addLayout(vb)

        self.setLayout(self.layout)

    @Slot(QAbstractButton)
    def displayMode(self, btn):
        self.displayText.setText(btn.description)

    def startSelectedMode(self):
        selectedBtn = self.buttons_group.checkedButton()
        widget = selectedBtn.constructor(self.mainwindow.currentUser)
        
        widget.closeRequested.connect(self.closeWidget)
        
        self.mainwindow.setWindowTitle("Consmaster" +
                        ' [' + selectedBtn.text().replace('\n', '') + ']')

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

    def closeWidget(self, widget):
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.setWindowTitle("Consmaster")
