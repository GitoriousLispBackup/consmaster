#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", out=sys.stderr)
    sys.exit(1)

class TermWidget(QPlainTextEdit) :
    """ A terminal-like Widget """

    #~ TODO: Finaliser backward
          #~ Implémenter lisp
    #~ WISHLIST: Implémenter historique avec up et down

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 100, 200)
        self.setWordWrapMode(QTextOption.WrapAnywhere)
        # self.read.connect(self.sendToInterpreter)
        self.startCursor = self.textCursor()
        self.i = 0

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

    def freezeAtCurrentPos(self):
        self.moveCursor(QTextCursor.End)
        self.startCursor = self.textCursor().position()

    @Slot(str)
    def out(self, s):
        self.appendPlainText(s + '\n')
        self.freezeAtCurrentPos()

    @Slot(str)
    def sendToInterpreter(self, expr):
        pass

    def printSelf(self) :
        line = self.document().findBlockByLineNumber(self.document().lineCount() - 1).text()
        #~ Remove prompt from line
        line = line[len(self.prompt):]
        self.appendPlainText(line)
        self.displayPrompt()

    def displayPrompt(self):
        self.i += 1
        self.insertPlainText("[{:d}]> ".format(self.i))
        self.freezeAtCurrentPos()

    def keyPressEvent(self, event):
        #~ Should be locked when processing

        if event.key() == Qt.Key_Return:
            line = self.document().toPlainText()[self.startCursor:]
            self.freezeAtCurrentPos()
            # self.read.emit(line)
            # hook
            self.out(line)
            self.displayPrompt()
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
        else:
            super().keyPressEvent(event)
