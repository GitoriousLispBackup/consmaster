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
from cm_globals import *


class SimpleLineEdit(QLineEdit):
    def get_expr(self):
        entry = self.text().strip()
        if not entry:
            QMessageBox.critical(self, 'Erreur', 'Vous devez entrer une expression valide.')
            return None
        return entry
    def reset(self):
        self.clear()

class EnonceTexte(QLabel):
    def set_expr(self, expr):
        self.setText(expr)

class EnonceGraphique(GlispWidget):
    def __init__(self):
        super().__init__()
        # self.setInteractive(False)
    def set_expr(self, expr):
        self.insert_expr(expr)


class WorkSpace(QWidget):
    getEntry = Signal(object)
    closeRequested = Signal(QWidget)
    
    def __init__(self, w_enonce, _in):
        super().__init__()

        layout = QVBoxLayout()

        label_en = QLabel('<b>Expression à convertir :</b>')
        label_in = QLabel('<b>Conversion :</b>')
        self._in = _in
        self.w_enonce = w_enonce
        self.validate_btn = QPushButton(QIcon("../icons/button_accept"), "Valider")
        self.validate_btn.setFixedHeight(35)
        self.next_btn = QPushButton(QIcon("../icons/go-next"), "Suivant")
        self.next_btn.setFixedHeight(35)
        self.close_btn = QPushButton(QIcon("../icons/cancel"), "Fermer")
        self.close_btn.setFixedHeight(35)
        
        topLayout = QVBoxLayout()
        topLayout.setAlignment(Qt.AlignTop)
        topLayout.addWidget(label_en)
        topLayout.addWidget(w_enonce)

        centerLayout = QVBoxLayout()
        centerLayout.setAlignment(Qt.AlignCenter)
        centerLayout.addWidget(label_in)
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

        self.validate_btn.clicked.connect(self.validateRequested)
        self.next_btn.clicked.connect(self.goNext)
        self.close_btn.clicked.connect(self.close)

    def validateRequested(self):
        expr = self._in.get_expr()
        if expr is not None:
            self.getEntry.emit(expr)

    def setController(self, controller):
        self.controller = controller
        controller.setWidget(self)
        
        controller.enonceChanged.connect(self.w_enonce.set_expr)
        controller.ok.connect(self.valided)
        self.getEntry.connect(controller.receive)
        self.goNext()

    def goNext(self):
        self.controller.next()
        self.validate_btn.setDisabled(False)
        self._in.reset()
        self._in.setFocus()

    def valided(self):
        self.validate_btn.setDisabled(True)

    def close(self):
        self.closeRequested.emit(self)


class TrainingWorkSpace(WorkSpace):
    pass

class ExerciceWorkSpace(WorkSpace):
    def goNext(self):
        self.next_btn.setDisabled(True)
        super().goNext()

    def valided(self):
        self.next_btn.setDisabled(False)
        super().valided()
        

######################################################
#                   constructors

def createTextMode(user):
    widget = TrainingWorkSpace(EnonceTexte(), SimpleLineEdit())
    userData = user.get_mode(NDN_CONV_MODE) if user else None
    controller = CmNDConvTrainingController(userData)
    widget.setController(controller)
    return widget

def createNormalToGraphicMode(user):
    widget = TrainingWorkSpace(EnonceTexte(), GraphicalLispGroupWidget())
    userData = user.get_mode(NG_CONV_MODE) if user else None
    controller = CmNTGConvTrainingController(userData)
    widget.setController(controller)
    return widget

def createGraphicToNormalMode(user):
    widget = TrainingWorkSpace(EnonceGraphique(), SimpleLineEdit())
    userData = user.get_mode(GN_CONV_MODE) if user else None
    controller = CmGTNConvTrainingController(userData)
    widget.setController(controller)
    return widget
