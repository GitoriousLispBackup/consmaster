#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from cm_main_menu import MainMenu

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

class Client(QMainWindow):
    """ Create client windows """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.createActions()
        self.createMenus()

        self.setGeometry(200, 200, 800, 620)
        self.setWindowTitle("Consmaster")
        self.setWindowIcon(QIcon("../icons/symbol"))

        self.central_widget = QStackedWidget()

        #~ Les widgets devraient pt être ajoutés à la volée,
        #~ en fonction de l'exo
        #~ plutôt qu'affichés directements
        #~ Dans un 1e temps, afficher directement tous les widgets

        self.menu_widget = MainMenu(self)
        self.central_widget.addWidget(self.menu_widget)

        self.setCentralWidget(self.central_widget)

        self.statusBar().showMessage('Ready')

        self.show()

    def createActions(self):
        self.quitAction = QAction(QIcon("../icons/application-exit"),
                "&Quitter", self, shortcut="Ctrl+Shift+Q",
                statusTip="Quitter l'application", triggered=self.close)
        #self.closeAction = QAction(QIcon("../icons/cancel"),
        #        "&Fermer", self, statusTip="Fermer l'exercice en cours")
        #self.closeAction.setEnabled(False)
        self.aboutAction = QAction(QIcon("../icons/help-browser"),
                "A &propos", self, shortcut="Ctrl+Shift+P",
                triggered=self.about)

    def createMenus(self):
        self.clientMenu = self.menuBar().addMenu("&Client")
        #~ Options de connexion
        self.clientMenu.addAction(self.quitAction)
        #self.clientMenu.addAction(self.closeAction)

        self.statMenu = self.menuBar().addMenu("&Statistiques")

        self.aboutMenu = self.menuBar().addMenu("&Aide")
        self.aboutMenu.addAction(self.aboutAction)      

    def about(self):
        QMessageBox.about(self, "A propos ConsMaster",
                "Maîtrisez les représentations de listes, en notations parenthésées, à point et en doublets graphiques.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())
