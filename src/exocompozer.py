#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os

from ec_editors import NewNormDotExo
from ec_editors import NewNormGraphExo

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

eq = {  "Normal - Dotted": "NormDot",
        "Normal - Graph": "NormGraph",
        "Graph - Normal": "GraphNorm"}


class Compozer(QMainWindow):
    """ Display all exercices listed in "save/" dir
        Double click to edit
        Create a new exercice w/ menus
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.createActions()
        self.createMenus()

        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Consmaster exercices composer")

        self.central_widget = self.createWidget()

        self.setCentralWidget(self.central_widget)

        self.populate()

        self.show()

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
        menu.addAction(self.quitAction)

    def createWidget(self):
        """ Create main tab widget """
        # ~ widget = QWidget()

        self.tabWidget = QTabWidget()

        self.tabND = QTableWidget()  # ~ Normal - Dotted
        self.tabND.setColumnCount(2)
        self.tabND.setHorizontalHeaderLabels(["Exercice", "Difficulté"])
        self.tabND.setColumnWidth(1, 120)
        self.tabND.horizontalHeader().setResizeMode(0, QHeaderView.Stretch);
        self.tabND.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabND.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabND.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tabNG = QTableWidget()  # ~ Normal - Graph
        self.tabNG.setColumnCount(2)
        self.tabNG.setHorizontalHeaderLabels(["Exercice", "Difficulté"])
        self.tabNG.setColumnWidth(1, 120)
        self.tabNG.horizontalHeader().setResizeMode(0, QHeaderView.Stretch);
        self.tabNG.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabNG.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabNG.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tabGN = QTableWidget()  # ~ Graph - Normal
        self.tabGN.setColumnCount(2)
        self.tabGN.setHorizontalHeaderLabels(["Exercice", "Difficulté"])
        self.tabGN.setColumnWidth(1, 120)
        self.tabGN.horizontalHeader().setResizeMode(0, QHeaderView.Stretch);
        self.tabGN.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabGN.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabGN.setEditTriggers(QAbstractItemView.NoEditTriggers)

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
        for dir in os.listdir("save/"):
            for file in os.listdir('save/'+dir):
                print(file)
                enonce = QTableWidgetItem(file.split("_")[1])
                #~ Custom class for sorting
                diff = IntQTableWidgetItem()
                diff.setData(Qt.EditRole, str(file.split("_")[0]))
    
                diff.setFlags(Qt.ItemIsSelectable)
    
                if dir == "NormDot":
                    self.tabND.setRowCount(self.tabND.rowCount() + 1)
                    self.tabND.setItem(self.tabND.rowCount() - 1, 0, enonce)
                    self.tabND.setItem(self.tabND.rowCount() - 1, 1, diff)
                    
                elif dir == "NormGraph":
                    self.tabNG.setRowCount(self.tabNG.rowCount() + 1)
                    self.tabNG.setItem(self.tabNG.rowCount() - 1, 0, enonce)
                    self.tabNG.setItem(self.tabNG.rowCount() - 1, 1, diff)
    
                elif dir == "GraphNorm":
                    self.tabGN.setRowCount(self.tabGN.rowCount() + 1)
                    self.tabGN.setItem(self.tabGN.rowCount() - 1, 0, enonce)
                    self.tabGN.setItem(self.tabGN.rowCount() - 1, 1, diff)

        self.tabND.sortItems(1)
        self.tabNG.sortItems(1)
        self.tabGN.sortItems(1)

    def displayDifficulty(self):
        difficulty = 5
        text = ""
        for i in range(0, difficulty):
            if i % 2 == 0:
                text += "*"
        return text

    def deleteExo(self):
        #~ Get file type
        exo_type = eq[self.tabWidget.tabText(self.tabWidget.currentWidget())]
        #~ Get file name
        exo_name = self.tabWidget.currentWidget().item(self.tabWidget.currentWidget().currentRow(), 0).text()
        #~ Get diff
        exo_diff = self.tabWidget.currentWidget().item(self.tabWidget.currentWidget().currentRow(), 1).text()
        #~ Remove file
        os.remove("save/{0}_{1}_{2}".format(exo_type, exo_diff, exo_name))

        self.tabWidget.currentWidget().removeRow(self.tabWidget.currentWidget().currentRow())

    def deleteAllExo(self):
        #~ Why delete all ?
        for i in range(0, self.tabWidget.count()):
            tab = self.tabWidget.widget(i)

            #~ Get file type
            exo_type = eq[self.tabWidget.tabText(i)]

            for row in range(0, tab.rowCount()):
                #~ Get file name
                exo_name = tab.item(row, 0).text()
                #~ Get diff
                exo_diff = tab.item(row, 1).text()
                #~ Remove file
                #~ print("save/{0}_{1}_{2}".format(exo_type, exo_diff, exo_name))
                os.remove("save/{0}_{1}_{2}".format(exo_type, exo_diff, exo_name))

                tab.removeRow(row)

    def editExo(self, item):
        """ Launch the correct widget to edit the exo """
        exo_type = eq[self.tabWidget.tabText(self.tabWidget.currentWidget().currentRow())]
        params = "self, item.text(), int(self.tabWidget.currentWidget().item(item.row(), 1).text())"
        class_call = "New{0}Exo({1})".format(exo_type, params)
        #~ C'est moche ça
        eval(class_call)

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
    def __lt__(self, other):
        return (int(self.data(Qt.EditRole)) < int(other.data(Qt.EditRole)))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = Compozer()
    sys.exit(app.exec_())
