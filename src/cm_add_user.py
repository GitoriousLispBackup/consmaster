#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_monitor import UserData
from cm_globals import CM_DATA

class AddUser(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        layout = QVBoxLayout()

        self.nameLineEdit = QLineEdit(self)
        self.emailLineEdit = QLineEdit(self)
        self.pwdLineEdit = QLineEdit(self)

        saveBtn = QPushButton("Sauvegarder", self)
        discardBtn = QPushButton("Quitter", self)

        formLayout = QFormLayout()
        formLayout.addRow("&Nom:", self.nameLineEdit)
        formLayout.addRow("&Email:", self.emailLineEdit)
        formLayout.addRow("&Password:", self.pwdLineEdit)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(saveBtn)
        buttonLayout.addWidget(discardBtn)

        layout.addLayout(formLayout)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        saveBtn.clicked.connect(self.accept)
        discardBtn.clicked.connect(self.reject)

    def accept(self):
        errMsg = []

        name = self.nameLineEdit.text().strip()
        if not name:
            errMsg.append('- Vous devez spéfifier un nom valide')
        elif name in {user.nick for user in self.data}:
            errMsg.append('- Ce nom existe déjà')

        email = self.emailLineEdit.text().strip()
        regex = QRegExp(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}', \
                Qt.CaseInsensitive, QRegExp.RegExp2)
        validator = QRegExpValidator(regex, self)
        if not email:
            errMsg.append('- Vous devez spécifier un email valide')
        elif validator.validate(email, 0)[0] != QValidator.Acceptable:
            errMsg.append('- Cette adresse email est invalide')
        elif email in {user.mail for user in self.data}:
            errMsg.append('- Cet email est déjà utilisé')

        pwd = self.pwdLineEdit.text().strip()
        if not pwd:
            errMsg.append('- Vous devez spécifier un mot de passe')

        if errMsg:
            QMessageBox.warning(self, 'Attention', '\n'.join(errMsg))
            return

        self.data.append(UserData(name, email, pwd))
        
        CM_DATA.sync()
        
        return super().accept()
