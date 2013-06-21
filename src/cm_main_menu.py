#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pickle
import textwrap

from cm_globals import *
from cm_free_mode import *
from cm_workspace import *
from cm_expr_generator import _cm_levels
from cm_exercice import CmExerciceBase, ex_load

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
        if mode.location:
            self.location = EXOS_DIR + '/' + mode.location


class ButtonList(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.toggled.connect(self.setMode)
        self.setMode(False)

    @Slot(bool)
    def setMode(self, checked):
        self.setText({True: '>', False: '<'}[checked])
        self.setToolTip({True: "cacher la liste d'exercices", False: "montrer la liste d'exercices"}[checked])


class ExosList(QWidget):
    shown = Signal()
    openExerciceRequested = Signal(CmExerciceBase)

    class QTableWidgetLevelItem(QTableWidgetItem):
        """ Custom QTableWidgetItem """
        def __init__(self, lvl):
            super().__init__('*' * lvl)
            self.setData(Qt.UserRole, lvl)
        def __lt__(self, other):
            return (self.data(Qt.UserRole) < other.data(Qt.UserRole))

    class QTableWidgetExoItem(QTableWidgetItem):
        """ Custom QTableWidgetItem """
        def __init__(self, name, filepath):
            super().__init__(name)
            self.setData(Qt.UserRole, ex_load(filepath))
    
    def __init__(self):
        super().__init__()
        label = QLabel("<b>Liste d'exercices</b>")
        self.lst = QTableWidget()
        self.lst.setColumnCount(2)
        self.lst.setHorizontalHeaderLabels([" Exercice ", "Niveau"])
        #self.lst.setColumnWidth(0, 100)
        self.lst.horizontalHeader().setResizeMode(0, QHeaderView.Stretch);
        self.lst.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lst.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lst.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lst.itemDoubleClicked.connect(self.openItem)
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.lst)
        self.setLayout(layout)

    def showEvent(self, event):
        self.shown.emit()
        super().showEvent(event)

    def reset(self):
        self.lst.clearContents()
        self.lst.setRowCount(0)

    def populate(self, mode, path):
        """
        Populate list from local directory.
        """
        self.reset()
        
        level = mode.currentLevel()
        # pouvoir refaire un exercice déjà fait ?
        # filtrer d'après le level
        for filename in os.listdir(path):
            lvl, _, name = filename.partition('_')
            n = self.lst.rowCount()
            self.lst.setRowCount(n + 1)
            self.lst.setItem(n, 0, ExosList.QTableWidgetExoItem(name, path + '/' + filename))
            self.lst.setItem(n, 1, ExosList.QTableWidgetLevelItem(int(lvl)))
        self.lst.sortItems(1)

    @Slot(QTableWidgetItem)
    def openItem(self, item):
        if isinstance(item, ExosList.QTableWidgetExoItem):
            self.openExerciceRequested.emit(item.data(Qt.UserRole))
        

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
        self.lstWidget.setFixedWidth(230)
        self.lstWidget.hide()
        self.lstWidget.shown.connect(self.refreshExosLst)
        self.lstWidget.openExerciceRequested.connect(self.startExercice)

        buttonsLayout = QHBoxLayout()
        launchButton = QPushButton("S'entrainer", self)
        launchButton.setFixedHeight(40)
        launchButton.clicked.connect(self.startSelectedMode)
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
                self.level.setValue(mode.currentLevel())
                self.exosButton.show()
                visible = self.exosButton.isChecked()
                self.lstWidget.setVisible(visible)
                if visible: self.lstWidget.populate(mode, btn.location) # refresh

    def refreshExosLst(self):
        btn = self.buttons_group.checkedButton()
        user = self.mainwindow.currentUser
        if user is not None:
            mode = user.get_mode(btn.id)
            self.lstWidget.populate(mode, btn.location)

    def startSelectedMode(self):
        """
        Start selected mode in training.
        """
        selectedBtn = self.buttons_group.checkedButton()
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
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.setWindowTitle("Consmaster")
        del widget.controller   # hack: force cotroller deleting, to remove interpreter if necessary
