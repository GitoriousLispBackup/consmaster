#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path

from ec_editors import NewNormDotExo, NewNormGraphExo, NewGraphNormExo
from cm_globals import EXOS_DIR
# from checkbox.properties import Int
# from ctypes.wintypes import INT

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

eq = {"Normal - Dotted": "NormDot",
        "Normal - Graph": "NormGraph",
        "Graph - Normal": "GraphNorm"}


class Compozer(QMainWindow):
    """ Display all exercices listed in "../save/" dir
        Double click to edit
        Create a new exercice w/ menus
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.checkDirs()

        self.createActions()
        self.createMenus()

        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Consmaster exercices composer")

        self.central_widget = self.createWidget()

        self.setCentralWidget(self.central_widget)

        self.populate()

        self.show()

    def checkDirs(self):
        """ Checks if valid path, create if not """
        if not os.path.exists(EXOS_DIR):
            os.mkdir(EXOS_DIR)
        for subdir in eq.values():
            path = EXOS_DIR + '/' + subdir
            if not os.path.exists(path):
                os.mkdir(path)

    def createActions(self):
        self.quitAction = QAction("Quitter", self, triggered=self.close)
        self.createDotNormExo = QAction("New Norm->Dotted", self, \
                                         triggered=self.newNormDotExo)
        self.createNormGraphExo = QAction("New Norm->Graph", self, \
                                           triggered=self.newNormGraphExo)
        self.createGraphNormExo = QAction("New Graph->Norm", self, \
                                           triggered=self.newGraphNormExo)
        self.createFreeExo = QAction("New Free", self, \
                                      triggered=self.newFreeExo)
        self.removeExo = QAction("Remove Entry", self, \
                                      triggered=self.deleteExo)
        self.removeAllExo = QAction("Remove _All_ Entry", self, \
                                      triggered=self.deleteAllExo)
        self.refresh = QAction("Refresh", self, \
                                              triggered=self.populate)

    def createMenus(self):
        menu = self.menuBar().addMenu("Menu")
        menu.addAction(self.createDotNormExo)
        menu.addAction(self.createNormGraphExo)
        menu.addAction(self.createGraphNormExo)
        menu.addAction(self.createFreeExo)
        menu.addSeparator()
        menu.addAction(self.removeExo)
        menu.addSeparator()
        menu.addAction(self.removeAllExo)
        menu.addSeparator()
        menu.addAction(self.refresh)
        menu.addSeparator()
        menu.addAction(self.quitAction)

    def createWidget(self):
        """ 
        Create main tab widget 
        Table have 3 cols: name, diff(int), diff(img)
        The 1st diff isn't display in list mode
        """
        # ~ widget = QWidget()

        self.tabWidget = QTabWidget()

        self.tabND = QTableWidget()  # ~ Normal - Dotted
        self.tabND.setColumnCount(3)
        self.tabND.setColumnHidden(1, True)
        self.tabND.setHorizontalHeaderLabels(["Exercice", "", "Difficulté"])
        self.tabND.setColumnWidth(1, 120)
        self.tabND.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tabND.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabND.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabND.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabND.editor = NewNormDotExo

        self.tabNG = QTableWidget()  # ~ Normal - Graph
        self.tabNG.setColumnCount(3)
        self.tabNG.setColumnHidden(1, True)
        self.tabNG.setHorizontalHeaderLabels(["Exercice", "", "Difficulté"])
        self.tabNG.setColumnWidth(1, 120)
        self.tabNG.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tabNG.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabNG.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabNG.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabNG.editor = NewNormGraphExo

        self.tabGN = QTableWidget()  # ~ Graph - Normal
        self.tabGN.setColumnCount(3)
        self.tabGN.setColumnHidden(1, True)
        self.tabGN.setHorizontalHeaderLabels(["Exercice", "", "Difficulté"])
        self.tabGN.setColumnWidth(1, 120)
        self.tabGN.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.tabGN.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabGN.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabGN.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabGN.editor = NewGraphNormExo

        self.tabWidget.addTab(self.tabND, "Normal - Dotted")
        self.tabWidget.addTab(self.tabNG, "Normal - Graph")
        self.tabWidget.addTab(self.tabGN, "Graph - Normal")

        self.tabND.itemDoubleClicked.connect(self.editExo)
        self.tabNG.itemDoubleClicked.connect(self.editExo)
        self.tabGN.itemDoubleClicked.connect(self.editExo)

        # ~ widget.addWidget(tabWidget)
        return self.tabWidget

    def clearAll(self):
        """ Clear the table, doesn't remove files"""
        self.tabND.clearContents()
        self.tabND.setRowCount(0)
        self.tabNG.clearContents()
        self.tabNG.setRowCount(0)
        self.tabGN.clearContents()
        self.tabGN.setRowCount(0)

    def populate(self):
        """ Populate tab widgets w/ files names """
        self.clearAll()
        for dirname in os.listdir(EXOS_DIR):
            for filename in os.listdir(EXOS_DIR + '/' + dirname):
                lvl, _, nm = filename.partition('_')

                name = QTableWidgetItem(nm)
                # ~ Custom class for sorting
                diff = IntQTableWidgetItem(lvl)
                diff.setFlags(Qt.ItemIsSelectable)
                graphDiff = QLabel(self.graphicalDiff(lvl))

                if dirname == "NormDot":
                    self.tabND.setRowCount(self.tabND.rowCount() + 1)
                    self.tabND.setItem(self.tabND.rowCount() - 1, 0, name)
                    self.tabND.setCellWidget(self.tabND.rowCount() - 1, 2, graphDiff)
                    self.tabND.setItem(self.tabND.rowCount() - 1, 1, diff)
                elif dirname == "NormGraph":
                    self.tabNG.setRowCount(self.tabNG.rowCount() + 1)
                    self.tabNG.setItem(self.tabNG.rowCount() - 1, 0, name)
                    self.tabNG.setCellWidget(self.tabNG.rowCount() - 1, 2, graphDiff)
                    self.tabNG.setItem(self.tabNG.rowCount() - 1, 1, diff)
                elif dirname == "GraphNorm":
                    self.tabGN.setRowCount(self.tabGN.rowCount() + 1)
                    self.tabGN.setItem(self.tabGN.rowCount() - 1, 0, name)
                    self.tabGN.setCellWidget(self.tabGN.rowCount() - 1, 2, graphDiff)
                    self.tabGN.setItem(self.tabGN.rowCount() - 1, 1, diff)
                else:
                    print("Dossiers inconnus rencontrés")

        self.tabND.sortItems(1)
        self.tabNG.sortItems(1)
        self.tabGN.sortItems(1)

    def graphicalDiff(self, lvl):
        """
            Display difficulty as images
        """
        base = int(float(lvl)) // 2
        frac = int(float(lvl)) % 2

        # Better to use QPixmap ?
        stars = '<img src=../icons/star.png /> ' * base
        stars += '<img src=../icons/star_h.png />' * frac

        return stars

    def deleteExo(self):
        """ Remoce an exo from list and from disk """
        # ~ Get file type
        exo_type = eq[self.tabWidget.tabText(self.tabWidget.currentWidget())]
        # ~ Get file name
        exo_name = self.tabWidget.currentWidget().item(self.tabWidget.currentWidget().currentRow(), 0).text()
        # ~ Get diff
        exo_diff = self.tabWidget.currentWidget().item(self.tabWidget.currentWidget().currentRow(), 1).text()
        # ~ Remove file
        os.remove("{}/{}/{}_{}".format(EXOS_DIR, exo_type, exo_diff, exo_name))

        self.tabWidget.currentWidget().removeRow(self.tabWidget.currentWidget().currentRow())

    def deleteAllExo(self):
        """ Dangerous one, use with caution """
        # ~ Why delete all ?
        for i in range(0, self.tabWidget.count()):
            tab = self.tabWidget.widget(i)

            # ~ Get file type
            exo_type = eq[self.tabWidget.tabText(i)]

            for row in range(0, tab.rowCount()):
                # ~ Get file name
                exo_name = tab.item(row, 0).text()
                # ~ Get diff
                exo_diff = tab.item(row, 1).text()
                # ~ Remove file
                os.remove("{}/{}/{}_{}".format(EXOS_DIR, exo_type, exo_diff, exo_name))

                tab.removeRow(row)

    def editExo(self, item):
        """ Launch the correct widget to edit the exo """
        editor = self.tabWidget.currentWidget().editor
        level = int(self.tabWidget.currentWidget().item(item.row(), 1).text())
        editor(self, item.text(), level)

    def newNormDotExo(self):
        """ New Norm <-> Dot exo """
        NewNormDotExo(self)

    def newNormGraphExo(self):
        """ New Norm -> Graph exo """
        NewNormGraphExo(self)

    def newGraphNormExo(self):
        """ New Graph -> Norm exo """
        NewGraphNormExo(self)

    def newFreeExo(self):
        pass


class IntQTableWidgetItem(QTableWidgetItem):
    """ Custom QTableWidget for sorting
        QTableWidget can't sort integers, must reimplement this """

    def __init__(self, txt):
        super().__init__(txt)
        self.setData(Qt.UserRole, int(txt))

    def __lt__(self, other):
        return (self.data(Qt.UserRole) < other.data(Qt.UserRole))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Compozer()
    sys.exit(app.exec_())
