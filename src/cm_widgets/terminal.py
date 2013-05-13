#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)

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

        self.palette = QPalette()
        self.textColor = "white"
        self.baseColor = "black"
        self.palette.setColor(QPalette.Text, self.textColor);
        self.palette.setColor(QPalette.Base, self.baseColor);
        self.setPalette(self.palette);

        #~ test
        self.setColor("black", "lightgray")
        self.displayPrompt()

    #~ Meilleure solution ?
    def setColor(self, text, base) :
        self.textColor = text
        self.baseColor = base
        self.palette.setColor(QPalette.Text, self.textColor);
        self.palette.setColor(QPalette.Base, self.baseColor);
        self.setPalette(self.palette);


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
