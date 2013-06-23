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
