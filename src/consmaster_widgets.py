#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)

class WidgetLayout(QWidget) :
    """ List of availables widgets"""

    def __init__(self, parent=None):
        super(WidgetLayout, self).__init__(parent)
        self.createWidgets()

    def createWidgets(self) :
        grid = QGridLayout()

        #~ Term-like widget
        termLabel = QLabel("Terminal")
        termEntry = TermWidget()
        termButton = QPushButton("Validate")
        grid.addWidget(termLabel, 0, 0, 1, 1)
        grid.addWidget(termEntry, 0, 1)
        grid.addWidget(termButton, 0, 5, 1, 1)
        termLabel.setBuddy(termEntry)

        termButton.clicked.connect(termEntry.printSelf)

        #~ A glisp form
        glispLabel = QLabel("Graph representation")
        glispEntry = GlispWidget()
        glispButton = QPushButton("Validate")
        glispClean = QPushButton("Effacer")
        grid.addWidget(glispLabel, 2, 0, 1, 1)
        grid.addWidget(glispEntry, 2, 1)
        vbox = QVBoxLayout()
        vbox.addWidget(glispButton)
        vbox.addWidget(glispClean)
        grid.addLayout(vbox, 2, 5, 1, 1)

        self.setLayout(grid)

class TermWidget(QPlainTextEdit) :
    """ A terminal-like Widget """

    #~ TODO: Finaliser backward
          #~ Implémenter lisp
    #~ WISHLIST: Implémenter historique avec up et down

    def __init__(self, parent=None):
        super(TermWidget, self).__init__(parent)
        self.i = 1
        self.prompt = ""
        self.startCursor = self.textCursor()
        self.setGeometry(0, 0, 100, 200)
        self.setWordWrapMode(QTextOption.WrapAnywhere)

        #~ Should be configurable
        palette = QPalette()
        palette.setColor(QPalette.Text, "white");
        palette.setColor(QPalette.Base, "black");
        self.setPalette(palette);

        self.displayPrompt()

    def printSelf(self) :
        line = self.document().findBlockByLineNumber(self.document().lineCount() - 1).text()
        #~ Remove prompt from line
        line = line[len(self.prompt):]
        self.appendPlainText(line)
        self.displayPrompt()

    def displayPrompt(self) :
        self.prompt = "({:d})> ".format(self.i)
        self.appendPlainText(self.prompt)
        self.startCursor = self.textCursor().position()
        self.i = self.i + 1

    def keyPressEvent(self, event):
        #~ Should be locked when processing

        #~ Avoid stranges things with ctrl
        if event.key() == Qt.Key_Return:
            self.printSelf()
        elif event.key() == Qt.Key_Up:
            #~ History up
            pass
        elif event.key() == Qt.Key_Down:
            #~ History down
            pass
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Left:
            #~ Ensure Backspace not erasing other lines
            if self.textCursor().position() > self.startCursor:
                super().keyPressEvent(event)
        else :
            super().keyPressEvent(event)

class GlispWidget(QGraphicsView) :
    """ Widget for graphical lisp """

    def __init__(self, parent=None):
        super(GlispWidget, self).__init__(parent)

        #~ Contient la repr glisp
        self.references = []

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 400, 300))
        self.scene.addRect(10,10,20,20)
        self = QGraphicsView(self.scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.show()

    def addCons(self) :
        pass

    def removeCons(self) :
        pass
