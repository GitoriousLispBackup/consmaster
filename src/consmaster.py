#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from cm_globals import *
from cm_main_menu import MainMenu
from cm_stats import *
from cm_add_user import *


class Client(QMainWindow):
    """ Create client windows """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = cm_load_data()

        if not self.data:
            print("Il est préférable de vous enregistrer afin de bénéficier des fonctions du suivi de progression.")
            #TODO : add dialog to add new users

        self.createMenus()

        self.setGeometry(200, 200, 800, 620)
        self.setWindowTitle("Consmaster")
        self.setWindowIcon(QIcon("../icons/symbol"))

        self.central_widget = QStackedWidget()

        self.menu_widget = MainMenu(self)
        self.central_widget.addWidget(self.menu_widget)

        self.setCentralWidget(self.central_widget)

        self.statusBar().showMessage('Ready')

        self.show()

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
        addUserAction = menu.addAction("&Ajouter un utilisateur")
        addUserAction.triggered.connect(self.addUser)

        statsAction = QAction(QIcon("../icons/help-browser"), # TODO: change this icon
                "&Stats", self, triggered=self.getStats)

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
        else:
            # TODO : prevent
            self.currentUser = None

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
                "Maîtrisez les représentations de listes, en notations parenthésées, à point et en doublets graphiques.")

    def getStats(self):
        StatsDialog(self.currentUser).exec_()

    def closeEvent(self, event):
        cm_save_data(self.data)
        super().closeEvent(event)
        


if __name__ == '__main__':
    cm_init()
    app = QApplication(sys.argv)
    client = Client()
    sys.exit(app.exec_())
