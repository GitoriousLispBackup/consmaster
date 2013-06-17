#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pickle
import textwrap

from cm_globals import *
from cm_free_mode import *
from cm_workspace import *
from cm_monitor import *
from cm_expr_generator import _cm_levels

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class ButtonMenu(QPushButton):
    def __init__(self, mode, parent):
        super().__init__('\n'.join(textwrap.wrap(mode.name, 10)), parent)
        self.description = open(mode.src, 'r', encoding='utf-8').read() if mode.src else 'information manquante sur ce mode'
        self.constructor = mode.constructor
        self.id = mode.name


class MainMenu(QWidget):
    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.basicMenu()

    #~ Basic and static menu
    def basicMenu(self):
        self.layout = QHBoxLayout()

        scrollContent = QWidget()

        #~ Layout in the scroll area
        vb = QVBoxLayout()
        self.buttons_group = QButtonGroup()
        self.buttons_group.setExclusive(True)

        for mode in MODES:
            btn = ButtonMenu(mode, scrollContent)
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

        self.level = QProgressBar()
        self.level.setMaximum(max(_cm_levels.keys()))
        self.level.setFormat('niveau %v/%m')
        self.displayText = QTextEdit()
        self.displayText.setReadOnly(True)
        launchButton = QPushButton("S'entrainer", self)
        launchButton.setFixedHeight(50)
        launchButton.clicked.connect(self.startSelectedMode)

        vb.addWidget(self.level)
        vb.addWidget(self.displayText)
        vb.addWidget(launchButton)
        self.layout.addLayout(vb)

        self.setLayout(self.layout)

    @Slot(QAbstractButton)
    def displayMode(self, btn):
        self.displayText.setText(btn.description)
        user = self.mainwindow.currentUser
        if user is not None:
            current_level = user.get_mode(btn.id).current_level()
            self.level.setValue(current_level)

    def startSelectedMode(self):
        selectedBtn = self.buttons_group.checkedButton()
        user = self.mainwindow.currentUser
        widget = selectedBtn.constructor(user.get_mode(selectedBtn.id) if user else None)
        
        widget.closeRequested.connect(self.closeWidget)
        
        self.mainwindow.setWindowTitle("Consmaster" +
                        ' [' + selectedBtn.text().replace('\n', '') + ']')

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

    def closeWidget(self, widget):
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.setWindowTitle("Consmaster")
