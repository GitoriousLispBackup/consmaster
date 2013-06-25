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
from cm_interm_repr import GraphExpr


class GraphicalLispGroupWidget(QWidget):
    """
    Group widget for graphical lisp widget,
    contain and connect additionals buttons
    and methods for usage.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.glisp_widget = GlispWidget(self)

        glispAddCons = QPushButton(QIcon("../icons/cons"), "Add Cons")
        glispAddAtom = QPushButton(QIcon("../icons/insert-atom"), "Add Atom")
        glispRemove = QPushButton("Remove")
        glispRemUnconnected = QPushButton("Clean")
        glispCleanAll = QPushButton(QIcon("../icons/clear"), "Clean All")
        glispAutolayout = QPushButton("Auto-layout")
        #~ glispCheck = QPushButton("Check")

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(glispAddCons)
        self.buttons_layout.addWidget(glispAddAtom)
        self.buttons_layout.addWidget(glispRemove)
        self.buttons_layout.addWidget(glispRemUnconnected)
        self.buttons_layout.addWidget(glispCleanAll)
        self.buttons_layout.addWidget(glispAutolayout)
        #~ self.buttons_layout.addWidget(glispCheck)

        #~ Actions
        glispAddCons.clicked.connect(self.glisp_widget.addCons)
        glispAddAtom.clicked.connect(self.glisp_widget.addAtom)
        glispRemove.clicked.connect(self.glisp_widget.removeSelectedItem)
        glispRemUnconnected.clicked.connect(self.glisp_widget.removeDisconnected)
        glispCleanAll.clicked.connect(self.glisp_widget.removeAll)
        glispAutolayout.clicked.connect(self.glisp_widget.autoLayout)
        #~ glispCheck.clicked.connect(self.glisp_widget.checkExpr)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.glisp_widget)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)

    def getExpr(self, with_layout=False):
        """
        get the lisp expression content in
        graphical widget (in intermediate
        format)
        """
        return self.glisp_widget.getExpr(with_layout)

    def setExpr(self, expr):
        self.glisp_widget.insert_expr(expr)

    def reset(self):
        """
        reset the graphical widget content
        """
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

    def getExpr(self, with_layout=False):
        """
        get intermediate representation of lisp expression
        connected to the root arrow
        """
        root = self.rootArrow.root
        # if root isn't connected
        if not isinstance(root, (GCons, GAtom)):
            QMessageBox.warning(self, 'Attention', "La flèche racine n'est connectée à aucun élément.\nVous devez la connecter avant de continuer.")
            return
        # if some elems are disconnected
        if len(self.orphans(root)) != 0:
            ret = QMessageBox.question(self, 'Attention', "Certains éléments ne sont pas reliés à l'arbre.\nVoulez vous continuer ?",
                                            QMessageBox.Yes, QMessageBox.No)
            if ret == QMessageBox.No:
                return
        # get intermediate lisp representation
        retval = self.scene.get_interm_repr(root)
        # add current layout, if required
        if with_layout: retval.layout = self.scene.get_current_layout()
        return retval

    #~ def checkExpr(self):
        #~ expr = self.getExpr()
        #~ if expr is not None:
            #~ print('level =', expr.level())
            #~ print('depth =', expr.depth())
            #~ print('proper =', expr.proper())
            #~ print('circ =', expr.circular())

    @Slot(object)
    def insert_expr(self, graph_expr):
        """
        insert lisp expression (in intermediate representation)
        in the graphical lisp widget
        """
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

        try:
            # if intermediate repr have a layout, use it
            positions = {dct[uid] : pos for uid, pos in graph_expr.layout.items()}
        except AttributeError:
            # else, use automatic layout
            positions = self.scene.get_automatic_layout(root)

        self.scene.apply_layout(positions)
        self.rootArrow.attach_to(root)

    def autoLayout(self):
        """
        auto-positionning tree connected to
        the root arrow
        """
        root = self.rootArrow.root
        if root is None: return
        positions = self.scene.get_automatic_layout(root)
        self.scene.apply_layout(positions)
        self.rootArrow.attach_to(root)

    def addCons(self):
        """
        Add graphical conse object into scene.
        """
        self.scene.addObj(GCons())

    def addAtom(self, value=None):
        """
        Add graphical atom object into scene.
        """
        self.scene.addObj(GAtom(value))

    def removeSelectedItem(self):
        """
        Remove selected item.
        """
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
        """
        return set of disconnected nodes in
        the graph
        """
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
