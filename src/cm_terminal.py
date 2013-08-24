#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

class TermWidget(QTextEdit):
    """ A terminal-like Widget """

    # ~ TODO: Finaliser backward
    read = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setGeometry(0, 0, 100, 200)
        self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.read.connect(self.updateHistory)
        self.setColor("black", "lightgray")
        self.setMinimumHeight(100)
        self.reset()

    def reset(self):
        """ Clean all text """
        self.i = 0
        self.hpos = 0
        self.history = []
        self.startCursor = self.textCursor()
        self.displayPrompt()
        # missing reset current text

    def setColor(self, textColor, baseColor):
        palette = QPalette()
        palette.setColor(QPalette.Text, textColor)
        palette.setColor(QPalette.Base, baseColor)
        self.setPalette(palette)

    def freezeAtCurrentPos(self):
        self.moveCursor(QTextCursor.End)
        self.startCursor = self.textCursor().position()

    @Slot(str)
    def out(self, s):
        self.append(s + '\n')
        self.freezeAtCurrentPos()

    @Slot(str)
    def updateHistory(self, line):
        self.history.append(line)
        self.hpos = len(self.history)

    def histNext(self):
        if self.hpos < len(self.history): self.hpos += 1
        return self.history[self.hpos] if 0 <= self.hpos < len(self.history) else ""

    def histPrev(self):
        if self.hpos >= 0: self.hpos -= 1
        return self.history[self.hpos] if 0 <= self.hpos < len(self.history) else ""

    def displayPrompt(self):
        self.i += 1
        self.insertPlainText("[{:d}]> ".format(self.i))
        self.freezeAtCurrentPos()

    def eraseLine(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor,
                                len(self.document().toPlainText()) - self.startCursor)
        cursor.removeSelectedText()

    def keyPressEvent(self, event):
        if self.textCursor().position() < self.startCursor:
            return

        if event.key() == Qt.Key_Return:
            line = self.document().toPlainText()[self.startCursor:]
            self.freezeAtCurrentPos()
            self.read.emit(line)
            # self.out(line)  # hook
            self.displayPrompt()
        elif event.key() == Qt.Key_Up:
            # ~ History up
            self.eraseLine()
            self.insertPlainText(self.histPrev())
        elif event.key() == Qt.Key_Down:
            # ~ History down
            self.eraseLine()
            self.insertPlainText(self.histNext())
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Left:
            # ~ Ensure Backspace not erasing other lines
            if self.textCursor().position() > self.startCursor:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
