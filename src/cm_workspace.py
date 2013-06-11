#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_lisp_graphic import *
from cm_controller import *


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

        self.next_btn.setDisabled(True)
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
        controller.ok.connect(self.get_ok)
        self.get_entry.connect(controller.receive)
        self.go_next()

    def go_next(self):
        self._in.reset()
        self.controller.next()
        self.next_btn.setDisabled(True)
        self._in.setFocus()

    def get_ok(self):
        self.next_btn.setDisabled(False)
        QMessageBox.information(self, 'Bravo!', 'Vous avez répondu correctement à cette question')

    @Slot(str)
    def get_error(self, msg):
        QMessageBox.critical(self, 'Erreur', msg, QMessageBox.Ok)

    def close(self):
        self.closeRequested.emit(self)


######################################################
#                   constructors

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
