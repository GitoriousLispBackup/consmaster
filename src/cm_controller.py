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

    def help(self, entry, enonce):
        if entry.isomorphic_to(enonce):
            QMessageBox.warning(None, "Erreur",
                    "Expression correctement formée, mais erreur sur un/des symbole/s.")
            return
        # TODO: add more help
        QMessageBox.warning(None, "Erreur",
                    "L'expression fournie est incorrecte.")


class CmNormalDottedConvController(CmBasicController):
    inv_methods = {'normal':'dotted_repr', 'dotted':'__repr__'}

    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # step 1 : check for parsing errors
        try:
            expr = Interpreter.parse(entry)
        except LispParseError as err:
            QMessageBox.warning(None, "Erreur",
                        "L'expression fournie est incorrecte.\n"
                        "Le parseur a retourné " + repr(err))
            return None
        # step 2 : check for conformity
        if not valid(entry, expr, self.typ):
            QMessageBox.warning(None, "Erreur",
                        "L'expression n'est pas conforme au format attendu.\n"
                        "Veuillez vérifier l'énoncé et le pretty-print.")
            return None
        return GraphExpr.from_lsp_obj(expr)


class CmNormalToGraphicController(CmBasicController):
    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # some verifications occurs at GUI level
        return entry

        
class CmGraphicToNormalController(CmBasicController):
    def __init__(self):
        super().__init__()

    def validate(self, entry):
        # step 1 : check for parsing errors
        try:
            expr = Interpreter.parse(entry)
        except LispParseError as err:
            QMessageBox.warning(None, "Erreur", 
                        "Erreur dans l'expression fournie.\n"
                        "Le parseur a retourné " + repr(err))
            return None
        # TODO : add adapted help to user
        return GraphExpr.from_lsp_obj(expr)


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
        self.interm_enonce = GraphExpr.from_lsp_obj(self.enonce)
        formatted = self.fmt(self.enonce)
        self.enonceChanged.emit(formatted)
        self.setCounterText.emit('{} / {}'.format(self.realised, self.total))

    @Slot(object)
    def receive(self, entry):
        interm = self.validate(entry)
        if not interm:
            self.updateData(0)
            return
        ok = interm == self.interm_enonce
        self.total += 1
        if ok:
            self.realised += 1
            self.ok.emit()
            QMessageBox.information(None, "Bravo !",
                    "Vous avez répondu correctement à cette question")
        else:
            self.help(interm, self.interm_enonce)
        self.setCounterText.emit('{} / {}'.format(self.realised, self.total))
        self.updateData(1 if ok else 0)

    def updateData(self, score):
        if self.userData:
            self.userData.addTrainingData(self.currentLevel, score)
            lvl = self.userData.currentLevel()
            if lvl > self.currentLevel:
                QMessageBox.information(None, "Bravo !",
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
        interm = self.validate(entry)
        if interm:  # des parties de la validation sont une grande aide, notament en mode NDN
            self.results.append(entry)
            self.ok.emit()  # bloque la touche de validation

    def next(self):
        self.exoNum += 1
        try:
            self.setCounterText.emit('exo {} / {}'.format(self.exoNum, self.total))
            self.enonce = next(self.enonceIter) # l'enonce n'est pas au format habituel
            formatted = self.fmt(self.enonce)   # side effect : set interm_repr
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
        return GraphExpr.from_lsp_obj(enonce)

################################################################################

class CmNDConvExerciceController(CmNormalDottedConvController, ExerciceMixin):
    def __init__(self, userData, src):
        CmNormalDottedConvController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        self.typ = enonce[0]
        expr = Interpreter.parse(enonce[1])
        self.interm_enonce = GraphExpr.from_lsp_obj(expr)
        return '<i>[' + self.typ + ']</i><br>' + enonce[1]

class CmNTGConvExerciceController(CmNormalToGraphicController, ExerciceMixin):
    def __init__(self, userData, src):
        CmNormalToGraphicController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        expr = Interpreter.parse(enonce)
        self.interm_enonce = GraphExpr.from_lsp_obj(expr)
        return enonce

class CmGTNConvExerciceController(CmGraphicToNormalController, ExerciceMixin):
    def __init__(self, userData, src):
        CmGraphicToNormalController.__init__(self)
        ExerciceMixin.__init__(self, src.lst)

    def fmt(self, enonce):
        self.interm_enonce = enonce
        return enonce
