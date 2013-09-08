#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os

from cm_lisp_graphic import *
from cm_terminal import *
from cm_controller import *
from cm_exercice import *
from cm_interpreter import Interpreter

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


EXOS_DIR = '../save'

class InfoWindows(QMessageBox):
    """ Simple informative modal message """
    def __init__(self, text):
        super().__init__()

        self.setText(text)

        self.setModal(True)
        self.exec_()


class NewNormDotExo(QDialog):
    """ Modal widget to create and edit Normal<->Dotted exercices """

    def __init__(self, parent, item="", diff=1):
        super().__init__(parent)

        self.diff = diff
        self.previousText = '(nil)'  # Used by verify system

        # ~ Used to remove the prev file when changing name/diff
        # ~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        # ~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

        # Mode réponse unique
        onceLabel = QLabel("Réponses uniques")
        self.onceMode = QCheckBox()

        list_add_btn = QPushButton("Ajouter")
        list_rm_btn = QPushButton("Supprimer")

        list_add_btn.clicked.connect(self.add)
        list_rm_btn.clicked.connect(self.delete)

        ok_btn = QPushButton("Sauvegarder et quitter")
        ok_btn.clicked.connect(self.save)
        abort_btn = QPushButton("Annuler")
        abort_btn.clicked.connect(self.close)

        self.list_widget = self.listExo()
        self.list_widget.itemClicked.connect(self.keep)
        self.list_widget.itemChanged.connect(self.verify)

        layout = QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addWidget(difficulty_label, 1, 0)
        layout.addWidget(self.difficulty_value, 1, 1)
        layout.addWidget(onceLabel, 2, 0)
        layout.addWidget(self.onceMode, 2, 1)
        layout.addWidget(self.list_widget, 5, 0, 1, 2)
        layout.addWidget(list_add_btn, 6, 0)
        layout.addWidget(list_rm_btn, 6, 1)
        layout.addWidget(ok_btn, 7, 0)
        layout.addWidget(abort_btn, 7, 1)

        self.setLayout(layout)

        if item is not "":
            self.load(item)

        self.setModal(True)
        self.exec_()

    def listExo(self):
        """ Create the table for listing """
        list_wid = QTableWidget()
        list_wid.setColumnCount(3)
        list_wid.setHorizontalHeaderLabels(["Once", "Dot", "Expression"])
        list_wid.setColumnWidth(0, 40)
        list_wid.setColumnWidth(1, 40)
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)
        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.setEditTriggers(QAbstractItemView.AllEditTriggers)

        return list_wid

    def add(self, value="(nil)", checked=False, once=False):
        """ Create a new entry with nedeed flags
        checked: False=Unchecked, True=Checked
        once = User have only one try or not [True/False]
        """
        qi = QTableWidgetItem(value)
        qi.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        qdot = QTableWidgetItem()
        qdot.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        qdot.setCheckState(Qt.Checked if checked else Qt.Unchecked)

        qonce = QTableWidgetItem()
        qonce.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        qonce.setCheckState(Qt.Checked if once else Qt.Unchecked)

        # ~ On ajoute une ligne
        # ~ Les rowCount ont un décalage de 1 O_o"
        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qonce)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 1, qdot)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 2, qi)

    def delete(self):
        """ Delete the current item """
        self.list_widget.removeRow(self.list_widget.currentRow())

    def keep(self, item):
        self.previousText = item.text()

    def verify(self, item):
        """ Check if not empty line """
        # ~ Should check for valid lisp expr
        if item.text() == "" and item.column() == 1:
            item.setText("(nil)")
        elif item.column() == 1:
            try:
                Interpreter.parse(item.text())
            except LispParseError as err:
                QMessageBox.warning(None, "Erreur",
                            "L'expression fournie est incorrecte.\n"
                            "Le parseur a retourné " + repr(err))
                print(item.text())
                self.list_widget.setFocus()
                item.setText(self.previousText)

    def iterAllItems(self):
        """ Create an iterator for lists' items """
        for i in range(self.list_widget.rowCount()):
            once = self.list_widget.item(i, 0)
            checkbox = self.list_widget.item(i, 1)
            textbox = self.list_widget.item(i, 2)
            yield (True if once.checkState() == Qt.Checked else False), ('dotted' if checkbox.checkState() == Qt.Checked else 'normal'), textbox.text()

    def save(self):
        """Save file on disk """
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            level = self.difficulty_value.value()
            name = self.name_field.text()
            filepath = '{}/NormDot/{}_{}'.format(EXOS_DIR, level, name)
            lst = list(self.iterAllItems())
            print(lst)
            ex_save(CmNDNExercice(name=name, level=level, lst=lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        """ Load a saved file """
        filepath = '{}/NormDot/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for once, mode, expr in exo.lst:
                print('load' , exo.lst)
                checked = mode == 'dotted'
                self.add(expr, checked, once)
        except IOError as e:
            print(e)
            self.done(0)



class NewNormGraphExo(QDialog):
    """ Modal widget to create and edit Normal->Graph exercices """

    def __init__(self, parent, item="", diff=1):
        super().__init__(parent)

        self.diff = diff
        self.previousText = '(nil)'  # Used by verify system

        # ~ To remove the prev file when changing name/diff
        # ~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        # ~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

         # Mode réponse unique
        onceLabel = QLabel("Réponses uniques")
        self.onceMode = QCheckBox()

        list_add_btn = QPushButton("Ajouter")
        list_rm_btn = QPushButton("Supprimer")
        list_add_btn.clicked.connect(self.add)
        list_rm_btn.clicked.connect(self.delete)

        ok_btn = QPushButton("Sauvegarder et quitter")
        ok_btn.clicked.connect(self.save)
        abort_btn = QPushButton("Annuler")
        abort_btn.clicked.connect(self.close)

        self.list_widget = self.listExo()
        self.list_widget.itemClicked.connect(self.keep)
        self.list_widget.itemChanged.connect(self.verify)

        layout = QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addWidget(difficulty_label, 1, 0)
        layout.addWidget(self.difficulty_value, 1, 1)
        layout.addWidget(onceLabel, 2, 0)
        layout.addWidget(self.onceMode, 2, 1)
        layout.addWidget(self.list_widget, 5, 0, 1, 2)
        layout.addWidget(list_add_btn, 6, 0)
        layout.addWidget(list_rm_btn, 6, 1)
        layout.addWidget(ok_btn, 7, 0)
        layout.addWidget(abort_btn, 7, 1)

        self.setLayout(layout)

        if item is not "":
            self.load(item)

        self.setModal(True)
        self.exec_()

    def listExo(self):
        """ Create the table for listing """
        list_wid = QTableWidget()
        list_wid.setColumnCount(2)
        list_wid.setHorizontalHeaderLabels(["Once", "Expression"])
        list_wid.setColumnWidth(0, 40)
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)

        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.setEditTriggers(QAbstractItemView.AllEditTriggers)

        list_wid.itemChanged.connect(self.verify)

        return list_wid

    def add(self, value="nil", once=False):
        """ Create an entry with nedeed flags """

        qi = QTableWidgetItem(value)
        qi.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        qonce = QTableWidgetItem()
        qonce.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        qonce.setCheckState(Qt.Checked if once else Qt.Unchecked)

        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qonce)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 1, qi)

    def delete(self):
        """ Delete the current item """
        self.list_widget.removeRow(self.list_widget.currentRow())

    def keep(self, item):
        self.previousText = item.text()

    def verify(self, item):
        """ Check if not empty line """
        # ~ Should check for valid lisp expr
        if (item.text() == ""):
            item.setText("nil")
        else:
            try:
                Interpreter.parse(item.text())
            except LispParseError as err:
                QMessageBox.warning(None, "Erreur",
                            "L'expression fournie est incorrecte.\n"
                            "Le parseur a retourné " + repr(err))
                print(item.text())
                self.list_widget.setFocus()
                item.setText(self.previousText)

    # ~ Cute iterator creator
    def iterAllItems(self):
        """ Create an iterator for lists' items """
        for i in range(self.list_widget.rowCount()):
            once = self.list_widget.item(i, 0)
            yield (True if once.checkState() == Qt.Checked else False), self.list_widget.item(i, 1).text()

    # ~ Save to file, need to be serialized
    def save(self):
        """Save file on disk """
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            name = self.name_field.text()
            level = self.difficulty_value.value()
            filepath = '{}/NormGraph/{}_{}'.format(EXOS_DIR, level, name)
            lst = list(self.iterAllItems())
            ex_save(CmNGExercice(name=name, level=level, lst=lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        """ Load a saved file """
        filepath = '{}/NormGraph/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for once, expr in exo.lst:
                self.add(expr, once)
        except IOError as e:
            print(e)
            self.done(0)


class NewGraphNormExo(QDialog):
    """ Modal widget to create and edit Graph->Norm exercices """

    def __init__(self, parent, item="", diff=1):
        super().__init__(parent)

        self.diff = diff

        # ~ To remove the prev file when changing name/diff
        # ~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        # ~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

         # Mode réponse unique
        onceLabel = QLabel("Réponses uniques")
        self.onceMode = QCheckBox()

        list_add_btn = QPushButton("Ajouter")
        list_rm_btn = QPushButton("Supprimer")
        list_add_btn.clicked.connect(self.add)
        list_rm_btn.clicked.connect(self.delete)

        ok_btn = QPushButton("Sauvegarder et quitter")
        ok_btn.clicked.connect(self.save)
        abort_btn = QPushButton("Annuler")
        abort_btn.clicked.connect(self.close)

        self.list_widget = self.listExo()

        layout = QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_field, 0, 1)
        layout.addWidget(difficulty_label, 1, 0)
        layout.addWidget(self.difficulty_value, 1, 1)
        layout.addWidget(onceLabel, 2, 0)
        layout.addWidget(self.onceMode, 2, 1)
        layout.addWidget(self.list_widget, 5, 0, 1, 2)
        layout.addWidget(list_add_btn, 6, 0)
        layout.addWidget(list_rm_btn, 6, 1)
        layout.addWidget(ok_btn, 7, 0)
        layout.addWidget(abort_btn, 7, 1)

        self.setLayout(layout)

        if item is not "":
            self.load(item)

        self.setModal(True)
        self.exec_()

    def listExo(self):
        """ Create the table for listing """
        list_wid = QTableWidget()
        list_wid.setColumnCount(2)
        list_wid.setHorizontalHeaderLabels(["Once", "Expression"])
        list_wid.setColumnWidth(0, 40)
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)
        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.itemDoubleClicked.connect(self.openEditGraph)

        return list_wid

    def openEditGraph(self, item):
        """ Open a modal graphic editor window """
        editor = GraphEditor(self, item)
        editor.exec_()

    def add(self, interm_expr=None, once=False):
        """ Create an entry with nedeed flags """

        value = 'nil' if interm_expr is None else str(interm_expr)
        qi = QTableWidgetItem(value)
        qi.setData(Qt.UserRole, interm_expr)
        qi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        qonce = QTableWidgetItem()
        qonce.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        qonce.setCheckState(Qt.Checked if once else Qt.Unchecked)

        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qonce)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 1, qi)

    def edit(self, expr, item):
        """ Edit an item """
        item.setData(Qt.UserRole, expr)
        item.setText(str(expr))

    def delete(self):
        """ Remove an item """
        self.list_widget.removeRow(self.list_widget.currentRow())

    # ~ Cute iterator creator
    def iterAllItems(self):
        """ Create an iterator for lists' items """
        for i in range(self.list_widget.rowCount()):
            once = self.list_widget.item(i, 0)
            yield (True if once.checkState() == Qt.Checked else False), self.list_widget.item(i, 1).data(Qt.UserRole)

    def save(self):
        """Save file on disk """
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            level = self.difficulty_value.value()
            name = self.name_field.text()
            filepath = '{}/GraphNorm/{}_{}'.format(EXOS_DIR, level, name)
            lst = list(self.iterAllItems())
            ex_save(CmGNExercice(name=name, level=level, lst=lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        """ Load a saved file """
        filepath = '{}/GraphNorm/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for once, expr in exo.lst:
                self.add(expr, once)
        except IOError as e:
            print(e)
            self.done(0)


class GraphEditor(QDialog):
    """ A modal graphic widget dialog to create a graphic representation """

    def __init__(self, parent, item):
        super().__init__(parent)

        self.parent = parent

        expr = item.data(Qt.UserRole)
        self.item = item

        self.setGeometry(200, 200, 820, 400)

        buttons_grp = QDialogButtonBox(self)
        save_btn = buttons_grp.addButton(QDialogButtonBox.Save)
        abort_btn = buttons_grp.addButton(QDialogButtonBox.Cancel)
        buttons_grp.accepted.connect(self.saveAndQuit)
        buttons_grp.rejected.connect(self.closeAndClean)

        self.widgetGraphical = GraphicalLispGroupWidget(self)
        self.widgetTerminal = TermWidget(self)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.widgetGraphical)
        splitter.addWidget(self.widgetTerminal)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, True)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(buttons_grp)
        self.setLayout(layout)

        self.setController(CmController(self.widgetTerminal))

        # HACK : force to setting size
        self.show()

        if expr:
            self.widgetGraphical.setExpr(expr)

    def saveAndQuit(self):
        """ Save current graphical editing and go back to list """
        expr = self.widgetGraphical.getExpr(True)
        if expr:  # Validity Check
            self.parent.edit(expr, self.item)
            self.closeAndClean()

    def closeAndClean(self):
        # Need to remove the controller every time
        self.close()
        del self.controller

    def setController(self, controller):
        self.controller = controller
        self.widgetTerminal.read.connect(controller.receive)
        controller.send.connect(self.widgetGraphical.setExpr)
