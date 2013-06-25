#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_globals import *
from cm_main_menu import MainMenu
from cm_stats import *
from cm_add_user import *


class Client(QMainWindow):
    """ Create client windows """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = cm_load_data()

        self.createMenus()

        self.setGeometry(200, 200, 800, 620)
        self.setWindowTitle("Consmaster")
        self.setWindowIcon(QIcon("../icons/cons"))

        self.central_widget = QStackedWidget()

        self.menu_widget = MainMenu(self)
        self.central_widget.addWidget(self.menu_widget)

        self.setCentralWidget(self.central_widget)

        self.statusBar().showMessage('Ready')

        if not self.data:
            self.currentUser = None
            QMessageBox.information(self, "Info",
                    "Il est préférable de vous enregistrer afin de bénéficier "
                    "des fonctionnalités du suivi de progression.")

    def createMenus(self):
        self.clientMenu = self.menuBar().addMenu("&Client")
        self.userMenu = self.menuBar().addMenu("&Utilisateurs")
        self.aboutMenu = self.menuBar().addMenu("&Aide")
        self.setBasicMenu(self.clientMenu)
        self.setUserMenu(self.userMenu)
        self.setHelpMenu(self.aboutMenu)

    def setBasicMenu(self, menu):
        quitAction = QAction(QIcon("../icons/application-exit"),
                "&Quitter", self, shortcut="Ctrl+Shift+Q",
                statusTip="Quitter l'application", triggered=self.close)
        # self.connectAction = self.clientMenu.addAction("Se connecter") 
        menu.addAction(quitAction)

    def setUserMenu(self, menu):
        addUserAction = menu.addAction(QIcon("../icons/add-user"),
                "&Ajouter un utilisateur")
        addUserAction.triggered.connect(self.addUser)

        statsAction = QAction(QIcon("../icons/chart"), # TODO: change this icon
                "&Statistiques", self, triggered=self.getStats)

        self.groupUser = QActionGroup(menu)  
        for user in self.data:
            setUsernameAction = menu.addAction(user.name)
            setUsernameAction.setCheckable(True)
            setUsernameAction.setData(user)
            setUsernameAction.toggled.connect(self.userChanged)
            self.groupUser.addAction(setUsernameAction)
        
        # select some user
        users = self.groupUser.actions()
        if users:
            users[0].setChecked(True)            

        menu.addSeparator()
        menu.addAction(addUserAction)
        menu.addSeparator()
        menu.addAction(statsAction)
        
    def setHelpMenu(self, menu):
        aboutAction = QAction(QIcon("../icons/help-browser"),
                "A &propos", self, shortcut="Ctrl+Shift+P",
                triggered=self.about)
        menu.addAction(aboutAction)


    @Slot(bool)
    def userChanged(self, checked):
        if checked:
            selected_action = self.groupUser.checkedAction()
            self.currentUser = selected_action.data()

    def addUser(self):
        dlg = AddUser(self.data, self)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            self.userMenu.clear()
            self.setUserMenu(self.userMenu)   

    def about(self):
        QMessageBox.about(self, "A propos ConsMaster",
                "Maîtrisez les représentations de listes, en notations parenthésées, "
                "à point et en doublets graphiques.")

    def getStats(self):
        # TODO: activer seulement si un user existe
        StatsDialog(self.currentUser).exec_()

    def closeEvent(self, event):
        cm_save_data(self.data)
        super().closeEvent(event)

################################################################################

if __name__ == '__main__':
    cm_init()
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())
