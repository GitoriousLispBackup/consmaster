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

class ExosList(QWidget):
    def __init__(self):
        super().__init__()
        label = QLabel("<b>Liste d'exercices</b>")
        self.lst = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.lst)
        self.setLayout(layout)

    def populate(self, mode):
        level = mode.current_level()
        # TODO: populate list from mode and level



class MainMenu(QWidget):
    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

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
        self.level.hide()
        
        self.displayText = QTextEdit()
        self.displayText.setReadOnly(True)
        self.lstWidget = ExosList()
        self.lstWidget.setFixedWidth(200)
        self.lstWidget.hide()

        buttonsLayout = QHBoxLayout()
        launchButton = QPushButton("S'entrainer", self)
        launchButton.setFixedHeight(40)
        launchButton.clicked.connect(self.startSelectedMode)
        self.exosButton = QPushButton("[*]", self)
        self.exosButton.setFixedSize(40, 40)
        self.exosButton.setCheckable(True)
        self.exosButton.hide()
        self.exosButton.toggled.connect(self.lstWidget.setVisible)
        buttonsLayout.addWidget(launchButton)
        buttonsLayout.addWidget(self.exosButton)

        viewLayout = QHBoxLayout()
        viewLayout.addWidget(self.displayText)
        viewLayout.addWidget(self.lstWidget)

        vb.addWidget(self.level)
        vb.addLayout(viewLayout)
        vb.addLayout(buttonsLayout)
        self.layout.addLayout(vb)

        self.setLayout(self.layout)

    @Slot(QAbstractButton)
    def displayMode(self, btn):
        self.displayText.setText(btn.description)
        user = self.mainwindow.currentUser
        if user is not None:
            try:
                # check if mode is available
                mode = user.get_mode(btn.id)
            except:
                self.level.hide()
                self.lstWidget.hide()
                self.exosButton.hide()
            else:
                self.level.show()
                self.level.setValue(mode.current_level())
                self.exosButton.show()
                self.lstWidget.populate(mode)
                self.lstWidget.setVisible(self.exosButton.isChecked())

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
