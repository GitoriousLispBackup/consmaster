#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import os

from cm_lisp_graphic import *
from cm_globals import EXOS_DIR
from cm_exercice import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

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

        #~ To remove the prev file when changing name/diff
        #~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        #~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

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
        list_wid.setHorizontalHeaderLabels(["Dot", "Expression"])
        list_wid.setColumnWidth(0, 40)
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)
        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.setEditTriggers(QAbstractItemView.AllEditTriggers)

        list_wid.itemChanged.connect(self.verify)

        return list_wid

    def add(self, value="nil", checked=False):
        """ Create an entry with nedeed flags
        checked: False=Unchecked, True=Checked
        """

        qi = QTableWidgetItem(value)
        qi.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        qdot = QTableWidgetItem()
        qdot.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        qdot.setCheckState(Qt.Checked if checked else Qt.Unchecked)

        # ~ On ajoute une ligne
        # ~ Les rowCount ont un décalage de 1 O_o"
        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qdot)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 1, qi)

    def delete(self):
        """ Delete the current item """
        self.list_widget.removeRow(self.list_widget.currentRow())

    def verify(self, item):
        # ~ Should check for valid lisp expr
        if (item.text() == "") and (item.column() == 1):
            item.setText("nil")

    # ~ Cute iterator creator
    def iterAllItems(self):
        for i in range(self.list_widget.rowCount()):
            checkbox = self.list_widget.item(i, 0)
            textbox = self.list_widget.item(i, 1)
            yield ('dotted' if checkbox.checkState() == Qt.Checked else 'normal'), textbox.text()
            
    def save(self):
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            level = self.difficulty_value.value()
            filepath = '{}/NormDot/{}_{}'.format(EXOS_DIR, level, self.name_field.text())
            lst = list(self.iterAllItems())
            ex_save(CmNDNExercice(level, lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        filepath = '{}/NormDot/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for mode, expr in exo.lst:
                checked = mode == 'dotted'
                self.add(expr, checked)
        except IOError as e:
            print(e)
            self.done(0)


class NewNormGraphExo(QDialog):
    """ Modal widget to create and edit Normal->Graph exercices """

    def __init__(self, parent, item="", diff=1):
        super().__init__(parent)

        self.diff = diff

        #~ To remove the prev file when changing name/diff
        #~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        #~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

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
        list_wid = QTableWidget()
        list_wid.setColumnCount(1)
        list_wid.setHorizontalHeaderLabels(["Expression"])
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)

        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.setEditTriggers(QAbstractItemView.AllEditTriggers)

        list_wid.itemChanged.connect(self.verify)

        return list_wid

    def add(self, value="nil"):
        """ Create an entry with nedeed flags """

        qi = QTableWidgetItem(value)
        qi.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qi)

    def delete(self):
        self.list_widget.removeRow(self.list_widget.currentRow())

    def verify(self, item):
        # ~ Should check for valid lisp expr
        if (item.text() == ""):
            item.setText("nil")

    # ~ Cute iterator creator
    def iterAllItems(self):
        for i in range(self.list_widget.rowCount()):
            yield self.list_widget.item(i, 0).text()

    # ~ Save to file, need to be serialized
    def save(self):
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            level = self.difficulty_value.value()
            filepath = '{}/NormGraph/{}_{}'.format(EXOS_DIR, level, self.name_field.text())
            lst = list(self.iterAllItems())
            ex_save(CmNGExercice(level, lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        filepath = '{}/NormGraph/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for expr in exo.lst:
                self.add(expr)
        except IOError as e:
            print(e)
            self.done(0)


class NewGraphNormExo(QDialog):
    """ Modal widget to create and edit Graph->Norm exercices """

    def __init__(self, parent, item="", diff=1):
        super().__init__(parent)

        self.diff = diff

        #~ To remove the prev file when changing name/diff
        #~ of a loaded file
        self.prev_file = ""

        self.setResult(0)
        self.finished.connect(parent.populate)

        self.setGeometry(300, 300, 500, 400)
        name_label = QLabel("Nom du fichier")
        self.name_field = QLineEdit()

        #~ Should be auto or not ?
        difficulty_label = QLabel("Difficulté")
        self.difficulty_value = QSpinBox()
        self.difficulty_value.setMinimum(1)
        self.difficulty_value.setMaximum(10)
        self.difficulty_value.setValue(self.diff)

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
        list_wid = QTableWidget()
        list_wid.setColumnCount(1)
        list_wid.setHorizontalHeaderLabels(["Expression"])
        list_wid.horizontalHeader().setStretchLastSection(True)
        list_wid.setSortingEnabled(False)
        list_wid.setSelectionMode(QAbstractItemView.SingleSelection)
        list_wid.itemDoubleClicked.connect(self.openEditGraph)

        return list_wid
    
    def openEditGraph(self, item):
        editor = GraphEditor(self, item)
        editor.exec_()

    def add(self, interm_expr=None):
        """ Create an entry with nedeed flags """

        value = 'nil' if interm_expr is None else str(interm_expr)
        qi = QTableWidgetItem(value)
        qi.setData(Qt.UserRole, interm_expr)
        qi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.list_widget.setRowCount(self.list_widget.rowCount() + 1)
        self.list_widget.setItem(self.list_widget.rowCount() - 1, 0, qi)
    
    def edit(self, expr, item):
        item.setData(Qt.UserRole, expr)
        item.setText(str(expr))

    def delete(self):
        self.list_widget.removeRow(self.list_widget.currentRow())

    def verify(self, item):
        # ~ Should check for valid lisp expr
        if (item.text() == ""):
            item.setText("nil")

    # ~ Cute iterator creator
    def iterAllItems(self):
        for i in range(self.list_widget.rowCount()):
            yield self.list_widget.item(i, 0).data(Qt.UserRole)

    def save(self):
        if not self.name_field.text():
            InfoWindows("Entrez un nom de fichier")
        elif self.list_widget.rowCount() == 0:
            InfoWindows("Entrez au moins un exercice")
        else:
            level = self.difficulty_value.value()
            filepath = '{}/GraphNorm/{}_{}'.format(EXOS_DIR, level, self.name_field.text())
            lst = list(self.iterAllItems())
            ex_save(CmGNExercice(level, lst), filepath)
            if self.prev_file and self.prev_file != filepath:
                os.remove(self.prev_file)
            self.prev_file = filepath  # need this ?
            self.done(1)

    def load(self, exo):
        filepath = '{}/GraphNorm/{}_{}'.format(EXOS_DIR, self.diff, exo)
        self.prev_file = filepath
        self.name_field.setText(exo)
        try:
            exo = ex_load(filepath)
            for expr in exo.lst:
                self.add(expr)
        except IOError as e:
            print(e)
            self.done(0)


class GraphEditor(QDialog):
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
        buttons_grp.rejected.connect(self.close)
        
        self.widget = GraphicalLispGroupWidget(self)
        
        layout = QGridLayout()
        layout.addWidget(self.widget, 0, 0)
        layout.addWidget(buttons_grp, 2, 0)

        self.setLayout(layout)

        # HACK : force to setting size
        self.show()

        if expr:
            self.widget.setExpr(expr)

    def saveAndQuit(self):
        expr = self.widget.getExpr(True)
        if expr: # Validity Check
            self.parent.edit(expr, self.item)
            self.close()
