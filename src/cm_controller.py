#!/usr/bin/python3
# -*- coding: utf-8 -*-


import re
import random


try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from pylisp import *
import pylisp.lisp_errors as lisp_errors
from lisp_errors import LispError, LispParseError

from cm_lisp_graphic import *
from cm_terminal import *
from cm_interpreter import Interpreter, GraphExpr
from cm_expr_generator import level_expr_gen


class CmController(QObject):
    send = Signal(object)

    def __init__(self, term):
        super().__init__()
        self.interpreter = Interpreter(out=term.out)

    @Slot(str)
    def receive(self, entry):
        retval = self.interpreter.eval(entry)
        if retval is not None:
            gexpr = GraphExpr.from_lsp_obj(retval)
            self.send.emit(gexpr)


############################################################
#               controllers for exercices

def valid(entry, expr, fmt='normal', strict=True):
    if not strict:
        entry = re.sub(r' +', ' ', entry)   # clean user entry
    method = {'dotted':'dotted_repr', 'normal':'__repr__'}[fmt]
    excepted = getattr(expr, method)()
    return entry == excepted


class CmBasicController(QObject):
    enonceChanged = Signal(object)
    setCounterText = Signal(str)
    ok = Signal()
    
    def __init__(self):
        super().__init__()
        self.interpreter = Interpreter()
        
    def setWidget(self, widget):
        self.widget = widget
        
    def help(self, entry, enonce):
        if entry.isomorphic_to(enonce):
            QMessageBox.warning(self.widget, "Erreur",
                    "Expression correctement formée, mais erreur sur un symbole.")
            return
        # TODO: add more help
        QMessageBox.warning(self.widget, "Erreur",
                    "L'expression fournie est incorrecte.")


class CmNormalDottedConvController(CmBasicController):
    inv_methods = {'normal':'dotted_repr', 'dotted':'__repr__'}

    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # step 1 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            QMessageBox.warning(self.widget, "Erreur",
                        "L'expression fournie est incorrecte.\n"
                        "Le parseur a retourné " + repr(err))
            return False
        # step 2 : check for conformity
        if not valid(entry, expr, self.typ):
            QMessageBox.warning(self.widget, "Erreur",
                        "L'expression n'est pas conforme au format attendu.\n"
                        "Veuillez vérifier l'énoncé et le pretty-print.")
            return False
        intermediate_enonce = GraphExpr.from_lsp_obj(self.enonce)
        interm = GraphExpr.from_lsp_obj(expr)
        if not interm == intermediate_enonce:
            self.help(interm, intermediate_enonce)
            return False
        else:
            return True


class CmNormalToGraphicController(CmBasicController):
    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # some verifications occurs at GUI level
        intermediate_enonce = GraphExpr.from_lsp_obj(self.enonce)
        if not entry == intermediate_enonce:
            self.help(entry, intermediate_enonce)
            return False
        else:
            return True

        
class CmGraphicToNormalController(CmBasicController):
    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # step 1 : check for parsing errors
        try:
            expr = self.interpreter.parse(entry)
        except LispParseError as err:
            QMessageBox.warning(self.widget, "Erreur", 
                        "Erreur dans l'expression fournie.\n"
                        "Le parseur a retourné " + repr(err))
            return False
        # TODO : add adapted help to user
        interm = GraphExpr.from_lsp_obj(expr)
        if not interm  == self.enonce_intermediate:
            self.help(interm, self.enonce_intermediate)
            return False
        else:
            return True

################################################################################

class TrainingMixin:
    def __init__(self, userData):
        self.userData = userData
        self.currentLevel = userData.currentLevel() if userData else 0
        self.enonceIter = level_expr_gen(self.currentLevel)
        self.total = 0
        self.realised = 0

    def next(self):
        self.enonce = next(self.enonceIter)
        formatted = self.fmt(self.enonce)
        self.enonceChanged.emit(formatted)
        self.setCounterText.emit('{} / {}'.format(self.realised, self.total))

    @Slot(object)
    def receive(self, entry):
        ok = self.validate(entry)
        self.total += 1
        if ok:
            self.realised += 1
            self.ok.emit()
            QMessageBox.information(self.widget, "Bravo !",
                    "Vous avez répondu correctement à cette question")
        self.setCounterText.emit('{} / {}'.format(self.realised, self.total))
        self.updateData(1 if ok else 0)

    def updateData(self, score):
        if self.userData:
            self.userData.addTrainingData(self.currentLevel, score)
            lvl = self.userData.currentLevel()
            if lvl > self.currentLevel:
                QMessageBox.information(self.widget, "Bravo !",
                    "Vous passez dorénavant au niveau " + str(lvl))
                self.currentLevel = lvl
                self.enonceIter = level_expr_gen(self.currentLevel)


class ExerciceMixin:
    def __init__(self, src):
        self.exoNum = 0
        self.total = len(src)
        self.enonceIter = iter(src) # TODO : make it work
        self.results = []
        
    @Slot(object)
    def receive(self, entry):
        self.results.append(entry)
        self.ok.emit()  # bloque la touche de validation

    def next(self):
        self.exoNum += 1
        try:
            self.setCounterText.emit('exo {} / {}'.format(self.exoNum, self.total))
            self.enonce = next(self.enonceIter) # l'enonce n'est pas au format habituel
            formatted = self.fmt(self.enonce)
            self.enonceChanged.emit(formatted)
        except StopIteration:
            # TODO : end of exercice
            # self.end.emit(results)
            print('end')

#########################################################################

class CmNDConvTrainingController(CmNormalDottedConvController, TrainingMixin):
    def __init__(self, userData):
        CmNormalDottedConvController.__init__(self)
        TrainingMixin.__init__(self, userData)

    def fmt(self, enonce):
        self.typ = random.choice(list(self.inv_methods.keys()))
        method_inv = self.inv_methods[self.typ]
        return '<i>[' + self.typ + ']</i><br>' + getattr(self.enonce, method_inv)()


class CmNTGConvTrainingController(CmNormalToGraphicController, TrainingMixin):
    def __init__(self, userData):
        CmNormalToGraphicController.__init__(self)
        TrainingMixin.__init__(self, userData)

    def fmt(self, enonce):
        return repr(enonce)


class CmGTNConvTrainingController(CmGraphicToNormalController, TrainingMixin):
    def __init__(self, userData):
        CmGraphicToNormalController.__init__(self)
        TrainingMixin.__init__(self, userData)

    def fmt(self, enonce):
        formatted = GraphExpr.from_lsp_obj(enonce)
        self.enonce_intermediate = formatted
        self.enonceChanged.emit(formatted)

################################################################################

class CmNDConvExerciceController(CmNormalDottedConvController, ExerciceMixin):
    def __init__(self, userData, src):
        CmNormalDottedConvController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        self.typ = enonce[0]
        return '<i>[' + self.typ + ']</i><br>' + enonce[1]

class CmNTGConvExerciceController(CmNormalToGraphicController, ExerciceMixin):
    def __init__(self, userData, src):
        CmNormalToGraphicController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        return enonce

class CmGTNConvExerciceController(CmGraphicToNormalController, ExerciceMixin):
    def __init__(self, userData, src):
        CmGraphicToNormalController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        return enonce
