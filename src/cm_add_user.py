#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)



class AddUser(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        
        layout = QVBoxLayout()
        
        self.nameLineEdit  = QLineEdit(self)
        self.emailLineEdit = QLineEdit(self)

        saveBtn = QPushButton("Sauvegarder", self)
        discardBtn = QPushButton("Quitter", self)

        formLayout = QFormLayout()
        formLayout.addRow("&Nom:", self.nameLineEdit)
        formLayout.addRow("&Email:", self.emailLineEdit)

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
            fail = True
            errMsg.append('- Vous devez spéfifier un nom valide')
        elif name in {user.name for user in self.data}:
            errMsg.append('- Ce nom existe déjà')
        email = self.emailLineEdit.text().strip()
        if not email: # TODO: add email validator
            errMsg.append('- Vous devez spéfifier un email valide')
        elif email in {user.mail for user in self.data}:
            errMsg.append('- Cet email est déjà utilisé')
        if errMsg:
            QMessageBox.warning(self, 'Attention', '\n'.join(errMsg))
            return
        self.data.append(UserData(name, email))
        return super().accept()
