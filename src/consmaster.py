#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)
    
from threading import Thread
from queue import Queue

from cm_globals import *
from cm_main_menu import MainMenu
from cm_stats import *
from cm_add_user import *
from cm_update import update_bdd
from cm_connexion import send_exercices
from cm_config import *


VERSION = '0.5'
AUTHORS = [
    'Josué Melka',
    'Calev Eliacheff',
    'David Calmeille'
]


class Client(QMainWindow):
    """ Create client windows """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.network_queue = Queue()
        self.t = Thread(target=self.worker)
        self.t.daemon = True
        self.t.start()
        
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

        self.network_queue.put(update_bdd)

    def worker(self):
        while True:
            item = self.network_queue.get()
            item()
            self.network_queue.task_done()

    def createMenus(self):
        self.clientMenu = self.menuBar().addMenu("&Client")
        self.userMenu = self.menuBar().addMenu("&Utilisateurs")
        self.aboutMenu = self.menuBar().addMenu("&Aide")
        self.setBasicMenu(self.clientMenu)
        self.setUserMenu(self.userMenu)
        self.setHelpMenu(self.aboutMenu)

    def setBasicMenu(self, menu):
        updateAction = QAction(QIcon("../icons/download"),
                "&Update", self, triggered=self.updateExosBdd)
        configAction = QAction(QIcon("../icons/configure"),
                "&Paramètres", self, shortcut="Ctrl+Shift+P",
                statusTip="Paramètres", triggered=self.networkConfig)
        quitAction = QAction(QIcon("../icons/application-exit"),
                "&Quitter", self, shortcut="Ctrl+Shift+Q",
                statusTip="Quitter l'application", triggered=self.close)
        
        menu.addAction(updateAction)
        menu.addAction(configAction)
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
            #TODO: est ce une façon correcte de faire ?
            self.network_queue.put(lambda: send_exercices(user))
            

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
            #TODO: add updating action ?
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
                "<h1>ConsMaster</h1> <h4>v " + VERSION + "</h4>" +
                "<p>Maîtrisez les représentations de listes, en notations parenthésées, "
                "à point et en doublets graphiques.</p>" +
                "<h4>Auteurs :</h4>" + 
                "<li><ul>" + '</ul><ul>'.join(AUTHORS) + '</ul></li>' )

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

    def networkConfig(self):
        form = Config(**CM_DATA['connexion_params'])
        ret = form.exec_()
        if ret == QDialog.Accepted:
            CM_DATA['connexion_params'] = {'host': form.hostname, 'port': form.port}
            CM_DATA.sync()

    def updateExosBdd(self):
        self.network_queue.put(update_bdd)
        
    def closeEvent(self, event):
        self.network_queue.join()
        CM_DATA.sync()
        CM_BDD.sync()
        print('cm: terminate')


###############################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec_())
