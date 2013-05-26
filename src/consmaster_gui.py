#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from consmaster_widgets import *

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

        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Consmaster")
        self.setWindowIcon(QIcon("../icons/symbol"))

        #~ Les widgets devraient pt être ajoutés à la volée,
        #~ en fonction de l'exo
        #~ plutôt qu'affichés directements
        #~ Dans un 1e temps, afficher directement tous les widgets

        #~ Temporaire, obligation du setCentral
        #~ TODO: Créer un placeholder en central à la place

        #~ widget = MainMenu()
        #~ self.setCentralWidget(widget)
        widget = WidgetsLayout()
        self.setCentralWidget(widget)

        self.statusBar().showMessage('Ready')

        self.show()

    def createActions(self):
        self.quitAction = QAction(QIcon("../icons/application-exit"),
                "&Quitter", self, shortcut="Ctrl+Shift+Q",
                statusTip="Quitter l'application", triggered=self.close)
        self.aboutAction = QAction(QIcon("../icons/help-browser"),
                "A &propos", self, shortcut="Ctrl+Shift+P",
                triggered=self.about)

    def createMenus(self):
        self.clientMenu = self.menuBar().addMenu("&Client")
        #~ Options de connexion
        #~ Options choix exos ?? ou questionBox au démarrage
        self.clientMenu.addAction(self.quitAction)

        self.aboutMenu = self.menuBar().addMenu("&Aide")
        self.aboutMenu.addAction(self.aboutAction)

    def about(self):
        QMessageBox.about(self, "A propos ConsMaster",
                "Maîtrisez les représentations de listes, en notations parenthésées, à point et en doublets graphiques.")

if __name__ == '__main__':

    app = QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())
