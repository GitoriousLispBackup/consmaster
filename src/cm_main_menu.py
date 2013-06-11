#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from cm_lisp_graphic import *
from cm_terminal import *
from cm_controller import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class ButtonMenu(QPushButton):
    def __init__(self, textSrc, func, name, parent):
        super().__init__(name, parent)
        self.description = open(textSrc, 'r', encoding='utf-8').read() if textSrc else 'information manquante sur ce mode'
        self.constructor = func


class SimpleLineEdit(QLineEdit):
    def get_expr(self):
        return self.text()
    def reset(self):
        self.clear()

class EnonceTexte(QLabel):
    def set_expr(self, expr):
        self.setText(expr)

class EnonceGraphique(GlispWidget):
    def set_expr(self, expr):
        self.insert_expr(expr)


class WorkSpace(QWidget):
    get_entry = Signal(object)
    closeRequested = Signal(QWidget)
    def __init__(self, enonce, _in):
        super().__init__()

        layout = QVBoxLayout()

        label_in = QLabel('<b>Expression à convertir :</b>')
        label_out = QLabel('<b>Conversion :</b>')
        self._in = _in
        self.enonce = enonce
        self.validate_btn = QPushButton(QIcon("../icons/button_accept"), "Valider")
        self.validate_btn.setFixedHeight(40)
        self.next_btn = QPushButton(QIcon("../icons/go-next"), "Suivant")
        self.next_btn.setFixedHeight(40)
        self.close_btn = QPushButton(QIcon("../icons/cancel"), "Fermer")
        self.close_btn.setFixedHeight(40)
        
        topLayout = QVBoxLayout()
        topLayout.setAlignment(Qt.AlignTop)
        topLayout.addWidget(label_in)
        topLayout.addWidget(enonce)

        centerLayout = QVBoxLayout()
        centerLayout.setAlignment(Qt.AlignCenter)
        centerLayout.addWidget(label_out)
        centerLayout.addWidget(_in)

        bottomLayout = QHBoxLayout()
        bottomLayout.setAlignment(Qt.AlignBottom)
        bottomLayout.addWidget(self.validate_btn)
        bottomLayout.addWidget(self.next_btn)
        bottomLayout.addSpacing(50)
        bottomLayout.addWidget(self.close_btn)

        layout.addLayout(topLayout)
        layout.addLayout(centerLayout)
        layout.addLayout(bottomLayout)

        self.setLayout(layout)

        self.validate_btn.clicked.connect(self.validate_requested)
        self.next_btn.clicked.connect(self.go_next)
        self.close_btn.clicked.connect(self.close)

    def validate_requested(self):
        expr = self._in.get_expr()
        self.get_entry.emit(expr)

    def set_controller(self, controller):
        self.controller = controller

        controller.enonce_changed.connect(self.enonce.set_expr)
        controller.error.connect(self.get_error)
        self.get_entry.connect(controller.receive)
        self.go_next()

    def go_next(self):
        self._in.reset()
        self._in.setFocus()
        self.controller.next()

    @Slot(str)
    def get_error(self, msg):
        QMessageBox.critical(self, 'Erreur', msg, QMessageBox.Ok)

    def close(self):
        self.closeRequested.emit(self)

class FreeMode(QWidget):
    closeRequested = Signal(QWidget)
    
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.graphical_group = GraphicalLispGroupWidget(self)
        self.terminal = TermWidget()
        self.close_btn = QPushButton(QIcon("../icons/cancel"), "Fermer")

        layout.addWidget(self.graphical_group)
        layout.addWidget(self.terminal)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

        self.terminal.setFocus()

        self.close_btn.clicked.connect(self.close)

    def set_controller(self, controller):
        self.controller = controller

        self.terminal.read.connect(controller.receive)
        controller.send.connect(self.graphical_group.glisp_widget.insert_expr)

    def close(self):
        self.closeRequested.emit(self)

# ne respecte pas certains trucs
def createFreeMode():
    widget = FreeMode()

    controller = CmController(widget.terminal)
    widget.set_controller(controller)
    return widget

def createTextMode():
    widget = WorkSpace(EnonceTexte(), SimpleLineEdit())

    controller = CmTextController()
    widget.set_controller(controller)
    return widget

def createNormalToGraphicMode():
    widget = WorkSpace(EnonceTexte(), GraphicalLispGroupWidget())

    controller = CmNormalToGraphicController()
    widget.set_controller(controller)

    return widget

def createGraphicToNormalMode():
    glispw = EnonceGraphique()
    glispw.setInteractive(False)

    widget = WorkSpace(glispw, SimpleLineEdit())

    controller = CmGraphicToNormalController()
    widget.set_controller(controller)

    return widget



class MainMenu(QWidget) :
    Modes = [
        ("Mode Libre", './mode-libre.html', createFreeMode),
        ("Standard \n<-> Dotted", None, createTextMode),
        ("Standard \n-> Graphique", None, createNormalToGraphicMode),
        ("Graphique \n-> Standard", None, createGraphicToNormalMode),
            ]

    """ Main menu creation/gestion

    The main menu is used as a laucher for all modules
    """
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.basicMenu()

    #~ Basic and static menu
    #~ TODO: should link to the correct text
    def basicMenu(self):
        self.layout = QHBoxLayout()

        scrollContent = QWidget()
        #~ self.resize(50,100)

        #~ Layout in the scroll area
        vb = QVBoxLayout()
        self.buttons_group = QButtonGroup()
        self.buttons_group.setExclusive(True)

        for name, src, func in MainMenu.Modes:
            btn = ButtonMenu(src, func, name, scrollContent)
            btn.setCheckable(True)
            btn.setFixedSize(120,120)
            vb.addWidget(btn)
            self.buttons_group.addButton(btn)
        self.buttons_group.buttonPressed.connect(self.displayMode)

        scrollContent.setLayout(vb)

        scroller = QScrollArea()
        scroller.setWidget(scrollContent)
        scroller.setFixedWidth(155)
        scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.layout.addWidget(scroller)

        #~ The text/hints display widget + his button
        vb = QVBoxLayout()
        self.displayText = QTextEdit()
        self.displayText.setReadOnly(True)

        launchButton = QPushButton("Démarrer", self)
        launchButton.setFixedHeight(50)
        launchButton.clicked.connect(self.startSelectedMode)

        vb.addWidget(self.displayText)
        vb.addWidget(launchButton)
        self.layout.addLayout(vb)

        self.setLayout(self.layout)

    @Slot(QAbstractButton)
    def displayMode(self, btn):
        self.displayText.setText(btn.description)

    def startSelectedMode(self):
        selectedBtn = self.buttons_group.checkedButton()
        widget = selectedBtn.constructor()
        
        widget.closeRequested.connect(self.closeWidget)

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

    def closeWidget(self, widget):
        self.mainwindow.central_widget.removeWidget(widget)

