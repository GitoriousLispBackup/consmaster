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
    """
    Input widget : subclass of QLineEdit that support
    getExpr() and reset() methods.
    """
    def getExpr(self):
        entry = self.text().strip()
        if not entry:
            QMessageBox.critical(self, 'Erreur', 'Vous devez entrer une expression valide.')
            return None
        return entry

    def reset(self):
        self.clear()

class EnonceTexte(QLabel):
    """
    Display widget: subclass of QLabel that support
    setExpr() method.
    """
    def setExpr(self, expr):
        self.setText(expr)

class EnonceGraphique(GlispWidget):
    """
    Display widget: subclass of GlispWidget that support
    setExpr() method.
    """
    def __init__(self, interactive=True):
        super().__init__()
        self.setInteractive(interactive)

    def setExpr(self, expr):
        self.insert_expr(expr)


class WorkSpace(QWidget):
    """
    A generic GUI widget class for training or exercices.
    Allow to connect the GUI to corresponding controller
    transparently.
    """

    getEntry = Signal(object)
    closeRequested = Signal(QWidget)

    def __init__(self, w_enonce, _in):
        """
        Constructor : get an statement and input widget,
        places them according to a generic layout style,
        with buttons for interact.
        """
        super().__init__()

        layout = QVBoxLayout()

        # creating and storing widgets
        label_en = QLabel('<b>Expression à convertir :</b>')
        self.label_counter = QLabel()
        self.w_enonce = w_enonce
        label_in = QLabel('<b>Conversion :</b>')
        self._in = _in
        self.validate_btn = QPushButton(QIcon("../icons/button_accept"), "Valider")
        self.validate_btn.setFixedHeight(35)
        self.next_btn = QPushButton(QIcon("../icons/go-next"), "Suivant")
        self.next_btn.setFixedHeight(35)
        self.close_btn = QPushButton(QIcon("../icons/cancel"), "Fermer")
        self.close_btn.setFixedHeight(35)

        lblLayout = QHBoxLayout()
        lblLayout.addWidget(label_en)
        lblLayout.addWidget(self.label_counter)
        topLayout = QVBoxLayout()
        topLayout.setAlignment(Qt.AlignTop)
        topLayout.addLayout(lblLayout)
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
        self.close_btn.clicked.connect(self.closeReq)
        #TODO: ajouter une connexion en cas de fermeture externe ?

    def validateRequested(self):
        """
        Get validation request (from validate button).
        Emit a signal to the controller.
        """
        expr = self._in.getExpr()
        if expr is not None:
            self.getEntry.emit(expr)

    def setController(self, controller):
        """
        Connect the passed controller to the corresponding
        signals and slots.
        """
        self.controller = controller
        controller.enonceChanged.connect(self.w_enonce.setExpr)
        controller.setCounterText.connect(self.label_counter.setText)
        controller.ok.connect(self.valided)
        controller.fail.connect(self.valided)
        controller.completed.connect(self.closeReq)
        self.getEntry.connect(controller.receive)
        self.goNext()  # ugly

    def goNext(self):
        """
        Go to next exercice.
        """
        self.controller.next()
        self.validate_btn.setEnabled(True)
        self._in.reset()
        self._in.setFocus()

    def valided(self):
        """
        Entry valided, disable validate button.
        """
        self.validate_btn.setDisabled(True)

    def closeReq(self):
        self.closeRequested.emit(self)


class TrainingWorkSpace(WorkSpace):
    """ Class specialisation for training workspace """
    pass

# TODO: ajouter un compteur faits/total
class ExerciceWorkSpace(WorkSpace):
    """ Class specialisation for exercices workspace """
    
    def closeReq(self):
        #TODO: demander si l'utilisateur veut vraiment arréter 
        #(s'il n'a pas fini seulement)
        self.controller.storeResults()
        super().closeReq()


######################################################
#                   constructors

def createTextMode(userData, uid=None):
    if not uid:
        widget = TrainingWorkSpace(EnonceTexte(), SimpleLineEdit())
        controller = CmNDConvTrainingController(userData)
    else:
        widget = ExerciceWorkSpace(EnonceTexte(), SimpleLineEdit())
        controller = CmNDConvExerciceController(userData, uid)
    widget.setController(controller)
    return widget

def createNormalToGraphicMode(userData, uid=None):
    if not uid:
        widget = TrainingWorkSpace(EnonceTexte(), GraphicalLispGroupWidget())
        controller = CmNTGConvTrainingController(userData)
    else:
        widget = ExerciceWorkSpace(EnonceTexte(), GraphicalLispGroupWidget())
        controller = CmNTGConvExerciceController(userData, uid)
    widget.setController(controller)
    return widget

def createGraphicToNormalMode(userData, uid=None):
    if not uid:
        widget = TrainingWorkSpace(EnonceGraphique(), SimpleLineEdit())
        controller = CmGTNConvTrainingController(userData)
    else:
        widget = ExerciceWorkSpace(EnonceGraphique(False), SimpleLineEdit())
        controller = CmGTNConvExerciceController(userData, uid)
    widget.setController(controller)
    return widget
