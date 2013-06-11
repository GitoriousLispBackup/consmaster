#!/usr/bin/python3
# -*- coding: utf-8 -*-


try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

from cm_lisp_obj import *
from cm_lisp_scene import LispScene
from cm_exercice import Encoder, dec as decoder
from cm_interm_repr import GraphExpr
import json


class GraphicalLispGroupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()

        self.glisp_widget = GlispWidget(self)

        glispAddCons = QPushButton("Add Cons")
        glispAddAtom = QPushButton("Add Atom")
        glispRemove = QPushButton("Remove")
        glispRemUnconnected = QPushButton("Clean")
        glispCleanAll = QPushButton("Clean All")
        glispAutolayout = QPushButton("Auto-layout")
        glispCheck = QPushButton("Check")
        #~ glispSave = QPushButton("Save")
        #~ glispLoad = QPushButton("Load")

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(glispAddCons)
        self.buttons_layout.addWidget(glispAddAtom)
        self.buttons_layout.addWidget(glispRemove)
        self.buttons_layout.addWidget(glispRemUnconnected)
        self.buttons_layout.addWidget(glispCleanAll)
        self.buttons_layout.addWidget(glispAutolayout)
        self.buttons_layout.addWidget(glispCheck)
        #~ self.buttons_layout.addWidget(glispSave)
        #~ self.buttons_layout.addWidget(glispLoad)

        #~ Actions
        glispAddCons.clicked.connect(self.glisp_widget.addCons)
        glispAddAtom.clicked.connect(self.glisp_widget.addAtom)
        glispRemove.clicked.connect(self.glisp_widget.removeSelectedItem)
        glispRemUnconnected.clicked.connect(self.glisp_widget.removeDisconnected)
        glispCleanAll.clicked.connect(self.glisp_widget.removeAll)
        glispAutolayout.clicked.connect(self.glisp_widget.autoLayout)
        glispCheck.clicked.connect(self.glisp_widget.checkExpr)
        #~ glispLoad.clicked.connect(self.glisp_widget.load)
        #~ glispSave.clicked.connect(self.glisp_widget.save)

        self.layout.addWidget(self.glisp_widget)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)

    def get_expr(self):
        return self.glisp_widget.get_expr()

    def reset(self):
        self.glisp_widget.removeAll()


class GlispWidget(QGraphicsView) :
    """ Widget for graphical lisp """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.arrow = None
        self.scene = LispScene()
        self.scene.setSceneRect(QRectF(0, 0, 650, 300))
        self.setRenderHint(QPainter.Antialiasing)

        self.scene.update()

        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        self.rootArrow = RootArrow()
        self.scene.addItem(self.rootArrow)

        self.show()

    def load(self):
        filename, ok = QFileDialog.getOpenFileName(self, "Load file", '.', "ConsMaster Files (*.cm)")
        with open(filename, 'r', encoding='utf-8') as fp:
            intermediate = json.load(fp, object_hook=decoder)
            self.insert_expr(intermediate)

    def save(self):
        rootItem = self.rootArrow.root
        if not isinstance(rootItem, (GCons, GAtom)):
            print('not root set. please set a root before saving')
            return
        
        intermediate = self.scene.get_interm_repr(rootItem)
        intermediate.layout = self.scene.get_current_layout()
        # print(intermediate.to_lsp_obj())
        
        filename, ok = QFileDialog.getSaveFileName(self, "Save file", '.', "ConsMaster Files (*.cm)")
        if not filename: return

        if not filename.endswith('.cm'):
            filename += '.cm'
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(intermediate, fp, cls=Encoder)

    def get_expr(self):
        root = self.rootArrow.root
        if root is None:
            ret = QMessageBox.warning(self, 'Attention', "La flèche racine n'est connectée à aucun élément.\nVous devez la connecter avant de continuer.")
            return
        if len(self.orphans(root)) != 0:
            ret = QMessageBox.question(self, 'Attention', "Certains éléments ne sont pas reliés à l'arbre.\nVoulez vous continuer ?",
                                            QMessageBox.Yes, QMessageBox.No)
            if ret == QMessageBox.No:
                return
        return self.scene.get_interm_repr(root)

    def checkExpr(self):
        expr = self.get_expr()
        if expr is not None:
            print('level =', expr.level())
            #~ print('depth =', expr.depth())
            #~ print('proper =', expr.proper())
            #~ print('circ =', expr.circular())

    @Slot(object)
    def insert_expr(self, graph_expr):
        if not graph_expr: return

        self.removeAll()

        dct = {}
        for k, v in graph_expr.graph.items():
            if GraphExpr.tag(v) == '#cons':
                g = GCons()
            elif GraphExpr.tag(v) == '#atom':
                if GraphExpr.value(v) == 'nil': continue
                g = GAtom(v[1])
            else:
                raise RuntimeError('not implemented')
            self.scene.addObj(g)
            dct[k] = g
        for k, g in dct.items():
            if isinstance(g, GCons):
                car_id, cdr_id = GraphExpr.value(graph_expr.graph[k])
                car, cdr = dct.get(car_id), dct.get(cdr_id)
                if car: self.scene.addPointer(Pointer(g, car, 'car'))
                if cdr: self.scene.addPointer(Pointer(g, cdr, 'cdr'))

        root = dct[graph_expr.root]

        positions = getattr(graph_expr, 'layout', None)
        if not positions:
            # Automatic layout
            positions = self.scene.get_automatic_layout(root)
        else:
            positions = {dct[uid] : pos for uid, pos in positions.items()}
            
        self.scene.apply_layout(positions)
        self.rootArrow.attach_to(root)

    def autoLayout(self):
        root = self.rootArrow.root
        if root is None: return
        # TODO : prevent if some elems are disconnected
        positions = self.scene.get_automatic_layout(root)
        self.scene.apply_layout(positions)
        self.rootArrow.attach_to(root)

    def addCons(self) :
        self.scene.addObj(GCons())

    def addAtom(self, value=None) :
        self.scene.addObj(GAtom(value))

    def removeSelectedItem(self) :
        for item in self.scene.selectedItems() :
            if isinstance(item, Pointer):
                self.scene.removePointer(item)
            elif isinstance(item, (GCons, GAtom)):
                if self.rootArrow.root == item:
                    self.rootArrow.detach()
                self.scene.removeObj(item)
            else:
                self.scene.removeItem(item)

    def orphans(self, root):
        tree = {} if root is None else self.scene.get_tree(root)
        return self.scene.graph.all_nodes().difference(tree.keys())

    def removeDisconnected(self):
        for orphan in self.orphans(self.rootArrow.root):
            self.scene.removeObj(orphan)

    def removeAll(self) :
        self.scene.reset()
        self.rootArrow.detach()
        self.scene.addItem(self.rootArrow)

    def mousePressEvent(self, mouseEvent):
        #~ Allows to create tmp arrows w/ right clic
        self.scene.clearSelection()
        if mouseEvent.button() == Qt.RightButton:
            pos = mouseEvent.pos()
            it = self.itemAt(pos)
            if isinstance(it, GCons) :
                self.arrow = ManualArrow(it, p1=pos, p2=pos)
                self.arrow.penColor = Qt.red
                self.scene.addItem(self.arrow)
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        #~ Redraw temp arrow according to mouse pos
        if self.arrow != None:
            newLine = QLineF(self.arrow.line().p1(), mouseEvent.pos())
            self.arrow.setLine(newLine)
        super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.arrow != None :
            for endItem in self.items(mouseEvent.pos()):
                if isinstance(endItem, (GCons, GAtom)):
                    p = Pointer(self.arrow.start, endItem, self.arrow.orig)
                    self.scene.addPointer(p)
                    break
            self.scene.removeItem(self.arrow)
            self.arrow = None
        super().mouseReleaseEvent(mouseEvent)
