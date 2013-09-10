#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_exercice import CmExerciceBase, ex_load
from cm_globals import CM_BDD


class ButtonList(QPushButton):
    """
    Special button, for displaying / hidding
    exercices list widget.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.toggled.connect(self.setMode)
        self.setMode(False)

    @Slot(bool)
    def setMode(self, checked):
        """
        Configure the button state.
        """
        self.setText({True: '>', False: '<'}[checked])
        self.setToolTip({True: "cacher la liste d'exercices", False: "montrer la liste d'exercices"}[checked])


class ExosList(QWidget):
    """
    Widget for displaying and manage exercices list.
    """
    openExerciceRequested = Signal(int)

    class QTableWidgetLevelItem(QTableWidgetItem):
        """
        Custom QTableWidgetItem for sorting.
        """
        def __init__(self, lvl):
            super().__init__(lvl)
            self.setData(Qt.UserRole, lvl)

        def __lt__(self, other):
            return self.data(Qt.UserRole) < other.data(Qt.UserRole)

    class QTableWidgetExoItem(QTableWidgetItem):
        """
        Custom QTableWidgetItem for save exercices data.
        """
        def __init__(self, name, uid):
            super().__init__(name)
            self.setData(Qt.UserRole, uid)

    class QLabelStar(QLabel):
        """
        Custom QTableWidgetItem for graphical display.
        """
        def __init__(self, lvl):
            super().__init__()
            stars = '<img src=../icons/star.png /> ' * (int(float(lvl)) // 2)
            stars += '<img src=../icons/star_h.png />' * (int(float(lvl)) % 2)
            self.setText(stars)

    def __init__(self):
        super().__init__()
        
        label = QLabel("<b>Liste d'exercices</b>")
        self.lst = QTableWidget()
        self.lst.setColumnCount(3)
        self.lst.setHorizontalHeaderLabels([" Exercice ", "Niveau", "Niveau"])
        self.lst.setColumnHidden(1, True)
        # self.lst.setColumnWidth(0, 100)
        self.lst.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.lst.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lst.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lst.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lst.itemDoubleClicked.connect(self.openItem)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.lst)
        self.setLayout(layout)

    def reset(self):
        """
        Reset the list widget.
        """
        self.lst.clearContents()
        self.lst.setRowCount(0)

    def populate(self, mode, exo_typ):
        """
        Populate list from local exercices directory.
        """
        self.reset()

        current_level = mode.currentLevel()
        # TODO: pouvoir refaire un exercice déjà fait ?
        for uid, exercice in CM_BDD.items():
            lvl = exercice.level
            if exercice.type == exo_typ: # and lvl <= current_level:
                n = self.lst.rowCount()
                self.lst.setRowCount(n + 1)
                self.lst.setItem(n, 0, self.QTableWidgetExoItem(exercice.name, uid))
                self.lst.setItem(n, 1, self.QTableWidgetLevelItem(lvl))
                self.lst.setCellWidget(n, 2, self.QLabelStar(lvl))
        self.lst.sortItems(1)

    @Slot(QTableWidgetItem)
    def openItem(self, item):
        if isinstance(item, ExosList.QTableWidgetExoItem):
            # emit a signal for open requested exercice
            self.openExerciceRequested.emit(item.data(Qt.UserRole))
