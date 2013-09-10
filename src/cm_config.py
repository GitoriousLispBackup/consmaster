#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class Config(QDialog):
    def __init__(self, host, port, parent=None):
        super().__init__(parent)
        self.hostname = host
        self.port = port

        self.setWindowTitle("Configuration du serveur")
        layout = QVBoxLayout()

        self.hostLine = QLineEdit(self)
        self.hostLine.setText(self.hostname)

        self.portLine = QLineEdit(self)
        self.portLine.setText(str(self.port))

        okBtn = QPushButton("Ok", self)
        discardBtn = QPushButton("Quitter", self)

        formLayout = QFormLayout()
        formLayout.addRow("Hostname:", self.hostLine)
        formLayout.addRow("Port:", self.portLine)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okBtn)
        buttonLayout.addWidget(discardBtn)

        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        okBtn.clicked.connect(self.accept)
        discardBtn.clicked.connect(self.reject)

    def accept(self):
        errMsg = []

        self.hostname = self.hostLine.text().strip()
        if not self.hostname:
            errMsg.append('- Hostname vide')

        self.port = self.portLine.text().strip()
        regex = QRegExp(r'[0-9]{1,5}', \
                Qt.CaseInsensitive, QRegExp.RegExp2)
        validator = QRegExpValidator(regex, self)
        if not self.port:
            errMsg.append('- Vous devez spécifier un port valide')
        elif validator.validate(self.port, 0)[0] != QValidator.Acceptable:
            errMsg.append('- Port invalide')
        else:
            pass

        if errMsg:
            QMessageBox.warning(self, 'Attention', '\n'.join(errMsg))
            return

        self.port = int(self.port)

        return super().accept()
