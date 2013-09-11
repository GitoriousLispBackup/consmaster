#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import json

from ec_editors import NewNormDotExo, NewNormGraphExo, NewGraphNormExo, EXOS_DIR, EC_BDD
from cm_exercice import decoder
from cm_globals import MODES


from server import *
from server.connexion import Connexion

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)



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

        #self.upload()
        self.populate()

        self.show()

    def checkDirs(self):
        """ Checks if valid path, create if not """
        if not os.path.exists(EXOS_DIR):
            os.mkdir(EXOS_DIR)

    def createActions(self):
        self.quitAction = QAction("Quitter", self, triggered=self.close)
        self.createDotNormExo = QAction("New Norm->Dotted", self, \
                                         triggered=self.newNormDotExo)
        self.createNormGraphExo = QAction("New Norm->Graph", self, \
                                           triggered=self.newNormGraphExo)
        self.createGraphNormExo = QAction("New Graph->Norm", self, \
                                           triggered=self.newGraphNormExo)

        self.removeExo = QAction("Remove Entry", self, \
                                      triggered=self.deleteExo)
        self.removeAllExo = QAction("Remove _All_ Entry", self, \
                                      triggered=self.deleteAllExo)
        self.refresh = QAction("Refresh", self, \
                                              triggered=self.populate)
        self.uploadAction = QAction("Upload", self, \
                                              triggered=self.upload)

    def createMenus(self):
        menu = self.menuBar().addMenu("Menu")
        menu.addAction(self.createDotNormExo)
        menu.addAction(self.createNormGraphExo)
        menu.addAction(self.createGraphNormExo)
        menu.addSeparator()
        menu.addAction(self.removeExo)
        menu.addSeparator()
        menu.addAction(self.removeAllExo)
        menu.addSeparator()
        menu.addAction(self.refresh)
        menu.addSeparator()
        menu.addAction(self.quitAction)
        menu = self.menuBar().addMenu("Serveur")
        menu.addAction(self.uploadAction)

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
        for nm, storage in EC_BDD.items():

            lvl = storage.level
            name = QTableWidgetItem(nm)
            
            if storage.id != None:
                name.setFlags(Qt.ItemIsSelectable)

            # ~ Custom class for sorting
            diff = IntQTableWidgetItem(lvl)
            diff.setFlags(Qt.ItemIsSelectable)
            graphDiff = QLabel(self.graphicalDiff(lvl))

            if storage.type == "__NDN__":
                self.tabND.setRowCount(self.tabND.rowCount() + 1)
                self.tabND.setItem(self.tabND.rowCount() - 1, 0, name)
                self.tabND.setCellWidget(self.tabND.rowCount() - 1, 2, graphDiff)
                self.tabND.setItem(self.tabND.rowCount() - 1, 1, diff)
            elif storage.type == "__NG__":
                self.tabNG.setRowCount(self.tabNG.rowCount() + 1)
                self.tabNG.setItem(self.tabNG.rowCount() - 1, 0, name)
                self.tabNG.setCellWidget(self.tabNG.rowCount() - 1, 2, graphDiff)
                self.tabNG.setItem(self.tabNG.rowCount() - 1, 1, diff)
            elif storage.type == "__GN__":
                self.tabGN.setRowCount(self.tabGN.rowCount() + 1)
                self.tabGN.setItem(self.tabGN.rowCount() - 1, 0, name)
                self.tabGN.setCellWidget(self.tabGN.rowCount() - 1, 2, graphDiff)
                self.tabGN.setItem(self.tabGN.rowCount() - 1, 1, diff)
            else:
                print("Elements inconnus rencontrés")

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
        """ Remove an exo from list and from disk """
        # ~ Get file name
        exo_name = self.tabWidget.currentWidget().item(self.tabWidget.currentWidget().currentRow(), 0).text()
        #TODO: delete it from server
        del EC_BDD[exo_name]

        EC_BDD.sync()

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
                # ~ Remove file
                del EC_BDD[exo_name]

                tab.removeRow(row)

        EC_BDD.sync()

    def editExo(self, item):
        """ Launch the correct widget to edit the exo """
        editor = self.tabWidget.currentWidget().editor
        level = self.tabWidget.currentWidget().item(item.row(), 1).value
        editor(self, item.text(), diff=level, overwrite=True)

        #TODO: empecher l'edition d'exercices deja uploade (id exists)
        #TODO: la protection contre l'overwrite ne fonctionne pas si l'user change le nom en mode edition...

    def newNormDotExo(self):
        """ New Norm <-> Dot exo """
        NewNormDotExo(self)

    def newNormGraphExo(self):
        """ New Norm -> Graph exo """
        NewNormGraphExo(self)

    def newGraphNormExo(self):
        """ New Graph -> Norm exo """
        NewGraphNormExo(self)


    """
        Networking
    """

    def upload(self):
        """ Upload all exercises to server's database """

        r = Login()
        retval = r.exec_()
        if retval != QDialog.Accepted:
            return

        data = {}

        data['action'] = 'creatExo'
        data['nickname'] = r.nick
        data['password'] = r.password

        for nm, storage in EC_BDD.items():
            if storage.id is not None:
                continue

            data['data'] = {'name': nm, 'type': storage.type, 'level': storage.level, 'raw': storage.serialized}
            entry = json.dumps(data)

            c = Connexion(entry)

            result = json.loads(c.result)
            # print(result)

            if result['status'] == 'success' and result['code'] == 'S_AEC':
                # retrieve server id and store it
                uid = result['data']['id']
                EC_BDD[nm] = storage._replace(id=uid)

        EC_BDD.sync()


class IntQTableWidgetItem(QTableWidgetItem):
    """ Custom QTableWidget for sorting
        QTableWidget can't sort integers, must reimplement this """

    def __init__(self, txt):
        super().__init__(txt)
        self.value = int(txt)

    def __lt__(self, other):
        return (self.value < other.value)


class Login(QDialog):
    """Simple login dialog"""
    def __init__(self):
        super().__init__()

        self.loginInput = QLineEdit(self)
        self.passwordInput = QLineEdit(self)

        layout = QVBoxLayout()

        okBtn = QPushButton("Valider", self)
        cancelBtn = QPushButton("Quitter", self)

        formLayout = QFormLayout()
        formLayout.addRow("&Nom d'utilisateur:", self.loginInput)
        formLayout.addRow("&Password:", self.passwordInput)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okBtn)
        buttonLayout.addWidget(cancelBtn)

        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)

        #self.exec_()

    def accept(self):
        self.nick = self.loginInput.text()
        self.password = self.passwordInput.text()

        if not self.nick or not self.password:
            QMessageBox.warning(self, 'Attention', 'Données invalides')
            return
        return super().accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Compozer()
    sys.exit(app.exec_())
