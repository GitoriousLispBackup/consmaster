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
    send = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.returnPressed.connect(self.receive)

    def receive(self):
        self.send.emit(self.text())
        self.clear()

        
class MainMenu(QWidget) :
    Modes = [
        ("Mode Libre", './mode-libre.html', 'createFreeMode'),
        ("Entrainement", None, ''),
        ("Standard \n<-> Dotted", None, 'createTextMode'),
        ("Standard \n-> Graphique", None, ''),
        ("Graphique \n-> Standard", None, ''),
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
            btn = ButtonMenu(src, getattr(self, func, None), name, scrollContent)
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

    Slot(QAbstractButton)
    def displayMode(self, btn):
        self.displayText.setText(btn.description)

    def startSelectedMode(self):
        selectedBtn = self.buttons_group.checkedButton()
        selectedBtn.constructor()

    def closeWidget(self, widget):
        self.mainwindow.central_widget.removeWidget(widget)
        self.mainwindow.closeAction.setEnabled(False)
        self.mainwindow.closeAction.triggered.disconnect()
        widget.destroy()
        del widget.controller  # why I must to manually do that ?

    def createFreeMode(self):
        widget = QWidget()

        layout = QVBoxLayout()

        graphical_group = GraphicalLispGroupWidget(widget)
        layout.addWidget(graphical_group)

        terminal = TermWidget()
        layout.addWidget(terminal)

        widget.setLayout(layout)

        widget.controller = CmController(terminal, graphical_group.glisp_widget)

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

        self.mainwindow.closeAction.triggered.connect(lambda: self.closeWidget(widget))
        self.mainwindow.closeAction.setEnabled(True)

        terminal.setFocus()

    def createTextMode(self):
        widget = QWidget()

        layout = QVBoxLayout()

        enonce = QLabel(widget)
        entry = SimpleLineEdit()
        
        layout.addWidget(enonce)
        layout.addWidget(entry)

        widget.setLayout(layout)

        widget.controller = CmTextController(enonce, entry)

        self.mainwindow.central_widget.addWidget(widget)
        self.mainwindow.central_widget.setCurrentWidget(widget)

        self.mainwindow.closeAction.triggered.connect(lambda: self.closeWidget(widget))
        self.mainwindow.closeAction.setEnabled(True)

        entry.setFocus()
