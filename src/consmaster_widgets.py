#!/usr/bin/python
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
        termEntry = termWidget()
        termButton = QPushButton("Validate")
        grid.addWidget(termLabel, 0, 0, 1, 1)
        grid.addWidget(termEntry, 0, 1)
        grid.addWidget(termButton, 0, 5, 1, 1)
        termLabel.setBuddy(termEntry)

        termButton.clicked.connect(termEntry.displayText)

        #~ A glisp form
        glispLabel = QLabel("Graph representation")
        glispEntry = glispWidget()
        glispButton = QPushButton("Validate")
        glispClean = QPushButton("Effacer")
        grid.addWidget(glispLabel, 2, 0, 1, 1)
        grid.addWidget(glispEntry, 2, 1)
        vbox = QVBoxLayout()
        vbox.addWidget(glispButton)
        vbox.addWidget(glispClean)
        grid.addLayout(vbox, 2, 5, 1, 1)

        self.setLayout(grid)

class termWidget(QPlainTextEdit) :
    """ A terminal-like Widget """

    #~ TODO: Finaliser backward
          #~ Implémenter lisp
    #~ WISHLIST: Implémenter historique avec up et down

    def __init__(self, parent=None):
        super(termWidget, self).__init__(parent)
        self.i = 1
        self.prompt = ""
        self.setGeometry(0, 0, 100, 200)

        #~ Should be configurable
        palette = QPalette()
        palette.setColor(QPalette.Text, "white");
        palette.setColor(QPalette.Base, "black");
        self.setPalette(palette);

        self.displayPrompt()

    def displayText(self) :
        #~ Will be a read-eval-print-loop
        line = self.document().findBlockByLineNumber(self.document().lineCount() - 1).text()
        #~ Remove prompt from line
        line = line[len(self.prompt):]
        self.appendPlainText(line)
        self.displayPrompt()

    def displayPrompt(self) :
        self.prompt = "({:d})> ".format(self.i)
        self.appendPlainText(self.prompt)
        self.i = self.i + 1

    def keyPressEvent(self, event):
        #~ Should be locked when processing
        if event.key() == Qt.Key_Return:
            self.displayText()
        elif event.key() == Qt.Key_Up:
            pass
        elif event.key() == Qt.Key_Down:
            pass
        elif event.key() == Qt.Key_Backspace :
            cursor = self.textCursor()
            if cursor.position() > len(self.prompt):
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                text = cursor.selection().toPlainText()
                cursor.removeSelectedText()
        else : self.insertPlainText(event.text())

class glispWidget(QGraphicsView) :
    """ Widget for graphical lisp """
    def __init__(self, parent=None):
        super(glispWidget, self).__init__(parent)

        scene = QGraphicsScene()
        scene.setSceneRect(QRectF(0, 0, 400, 300))
        self.glispView = QGraphicsView(scene)
        self.glispView.setAlignment(Qt.AlignLeft|Qt.AlignTop)
