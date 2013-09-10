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
from cm_update import update_bdd


class Client(QMainWindow):
    """ Create client windows """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentUser = None
        self.data = CM_DATA['userlist']

        self.initStatusBar()
        self.createMenus()

        self.setGeometry(200, 200, 800, 620)
        self.setWindowTitle("Consmaster")
        self.setWindowIcon(QIcon("../icons/cons"))

        self.central_widget = QStackedWidget()
        self.central_widget.currentChanged.connect(self.showOrHideUserMenu)

        self.menu_widget = MainMenu(self)
        self.central_widget.addWidget(self.menu_widget)

        self.setCentralWidget(self.central_widget)

        if not self.data:
            QMessageBox.information(self, "Info",
                    "Il est préférable de vous enregistrer afin de bénéficier "
                    "des fonctionnalités du suivi de progression.")

        update_bdd()

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

        if self.data:
            statsAction = QAction(QIcon("../icons/chart"),  # TODO: change this icon
                "&Statistiques", self, triggered=self.getStats)

        self.groupUser = QActionGroup(menu)
        for user in self.data:
            setUsernameAction = menu.addAction(user.nick)
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
        if self.data:
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
            self.currentUser.register()
        self.updateStatusBar()

    def addUser(self):
        dlg = AddUser(self.data, self)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            self.userMenu.clear()
            self.setUserMenu(self.userMenu)

    def showOrHideUserMenu(self, index):
        """ Do not show if playing """

        if index == 0:
            self.groupUser.setVisible(True)
        else:
            self.groupUser.setVisible(False)

    def about(self):
        QMessageBox.about(self, "A propos ConsMaster",
                "Maîtrisez les représentations de listes, en notations parenthésées, "
                "à point et en doublets graphiques.")

    def getStats(self):
        # TODO: activer seulement si un user existe
        StatsDialog(self.currentUser).exec_()

    def initStatusBar(self):
        self.userWid = QLabel()
        self.servWid = QLabel()
        self.servWid.setAlignment(Qt.AlignRight)
        self.statusBar().addWidget(self.userWid)
        self.statusBar().addPermanentWidget(self.servWid)
        self.updateStatusBar()

    def updateStatusBar(self):
        connected = 0  # For testing

        if self.currentUser:
            userLabel = 'Enregistré : {}'.format(self.currentUser.nick)
        else:
            userLabel = 'Mode anonyme'

        if connected:
            servLabel = 'Connecté au serveur'
        else:
            servLabel = 'Déconnecté du serveur'

        self.userWid.setText(userLabel)
        self.servWid.setText(servLabel)

###############################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())
