#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pickle
import textwrap

from cm_globals import *
from cm_free_mode import *
from cm_workspace import *
from cm_expr_generator import _cm_levels
from cm_exercice_list import ExosList, ButtonList
from cm_exercice import CmExerciceBase

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class ButtonMenu(QPushButton):
    def __init__(self, mode):
        super().__init__('\n'.join(textwrap.wrap(mode.name, 10)))
        self.description = open(mode.src, 'r', encoding='utf-8').read() if mode.src else 'information manquante sur ce mode'
        self.constructor = mode.constructor
        self.id = mode.name
        if mode.location:
            self.location = EXOS_DIR + '/' + mode.location

class MainMenu(QWidget):
    """
    Main menu creation / gestion.
    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow

        self.layout = QHBoxLayout()

        # ~ Layout in the scroll area
        vb = QVBoxLayout()
        self.buttons_group = QButtonGroup()
        self.buttons_group.setExclusive(True)
        # add buttons for all exists modules
        for mode in MODES:
            btn = ButtonMenu(mode)
            btn.setCheckable(True)
            btn.setFixedSize(120, 120)
            vb.addWidget(btn)
            self.buttons_group.addButton(btn)
        self.buttons_group.buttonClicked.connect(self.displayMode)

        scrollContent = QWidget()  # container widget
        scrollContent.setLayout(vb)
        scroller = QScrollArea()
        scroller.setWidget(scrollContent)
        scroller.setFixedWidth(155)
        # scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.layout.addWidget(scroller)

        # ~ The text/hints display widget + his button
        vb = QVBoxLayout()
        # progress bar for displaying user's current level
        self.level = QProgressBar()
        self.level.setMaximum(max(_cm_levels.keys()))
        self.level.setFormat('niveau %v/%m')
        self.level.hide()
        # widget for displaying informations about selected module
        self.displayText = QTextEdit()
        self.displayText.setReadOnly(True)
        # list widget: manage exercices of selected module
        self.lstWidget = ExosList()
        self.lstWidget.setFixedWidth(230)
        self.lstWidget.hide()
        self.lstWidget.openExerciceRequested.connect(self.startExercice)

        buttonsLayout = QHBoxLayout()
        # button for start training mode of selected module
        launchButton = QPushButton("S'entrainer", self)
        launchButton.setFixedHeight(40)
        launchButton.clicked.connect(self.startSelectedMode)
        # button for display exercices list, if exists
        self.exosButton = ButtonList(self)
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
        """
        Display informations about the selected mode.
        If exercices are supported by this module, display
        widgets of corresponding mode.
        """
        self.displayText.setText(btn.description)
        user = self.mainwindow.currentUser
        if user is not None:  # if an user is selected
            try:
                # check if mode is available
                mode = user.get_mode(btn.id)
            except:
                self.level.hide()
                self.lstWidget.hide()
                self.exosButton.hide()
            else:
                self.level.show()
                self.level.setValue(mode.currentLevel())
                self.exosButton.show()
                self.lstWidget.setVisible(self.exosButton.isChecked())
                self.lstWidget.populate(mode, btn.location)  # refresh exercices list

    def startSelectedMode(self):
        """
        Start selected mode in training.
        """
        selectedBtn = self.buttons_group.checkedButton()
        if selectedBtn is None:
            QMessageBox.information(self, 'Attention', 'Aucun mode selectionné.\n'
                                                       'Vous devez choisir un mode avant de le lancer.')
            return

        user = self.mainwindow.currentUser
        try:
            widget = selectedBtn.constructor(user.get_mode(selectedBtn.id))
        except:
            widget = selectedBtn.constructor(None)
        widget.closeRequested.connect(self.closeWidget)

        self.mainwindow.setWindowTitle("Consmaster" +
                        ' [' + selectedBtn.text().replace('\n', '') + ']')

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

    @Slot(CmExerciceBase)
    def startExercice(self, exo):
        """
        Start selected exercice.
        """
        selectedBtn = self.buttons_group.checkedButton()
        user = self.mainwindow.currentUser
        widget = selectedBtn.constructor(user.get_mode(selectedBtn.id), exo)

        widget.closeRequested.connect(self.closeWidget)

        self.mainwindow.setWindowTitle("Consmaster" +
                        ' [' + selectedBtn.text().replace('\n', '') + ']')

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

    @Slot(QWidget)
    def closeWidget(self, widget):
        """
        Close the current worspace widget.
        """
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.setWindowTitle("Consmaster")
        del widget.controller  # hack: force cotroller deleting, to remove interpreter if necessary
