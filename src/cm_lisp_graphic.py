#!/usr/bin/python3
# -*- coding: utf-8 -*-


from cm_graph import *
from cm_lisp_obj import *

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)

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
        #glispSave = QPushButton("Save")
        #glispLoad = QPushButton("Load")

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(glispAddCons)
        self.buttons_layout.addWidget(glispAddAtom)
        self.buttons_layout.addWidget(glispRemove)
        self.buttons_layout.addWidget(glispRemUnconnected)
        self.buttons_layout.addWidget(glispCleanAll)
        #self.buttons_layout.addWidget(glispSave)
        #self.buttons_layout.addWidget(glispLoad)

        #~ Actions
        glispAddCons.clicked.connect(self.glisp_widget.addCons)
        glispAddAtom.clicked.connect(self.glisp_widget.addAtom)
        glispRemove.clicked.connect(self.glisp_widget.removeSelectedItem)
        glispRemUnconnected.clicked.connect(self.glisp_widget.removeDisconnected)
        glispCleanAll.clicked.connect(self.glisp_widget.removeAll)
        #glispLoad.clicked.connect(self.glisp_widget.load)
        #glispSave.clicked.connect(self.glisp_widget.save)

        self.layout.addWidget(self.glisp_widget)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)


class LispScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = DiGraph()
        
    def addObj(self, obj):
        self.graph.add_vertex(obj)
        self.addItem(obj)

    def addPointer(self, pointer):
        self.graph.add_edge(pointer.startItem, pointer.endItem, key=pointer.orig, arrow=pointer)
        self.addItem(pointer)

    def removeObj(self, obj):
        all_edges = [data['arrow'] for u, v, k, data in self.graph.outcoming_edges(obj)]
        all_edges += [data['arrow'] for u, v, k, data in self.graph.incoming_edges(obj)]

        # print('edges :', all_edges)
        for arrow in all_edges:
            self.removePointer(arrow)
        self.graph.remove_vertex(obj)
        self.removeItem(obj)
        
    def removePointer(self, pointer):
        self.graph.remove_edge(pointer.startItem, pointer.endItem, pointer.orig)
        self.removeItem(pointer)

    def getEdgesFrom(self, vertex, key=None):
        # WARNING : dans un sens seulement
        return [data['arrow'] for u, v, k, data in self.graph.outcoming_edges(vertex, key)]

    def reset(self):
        for item in self.items() :
            self.removeItem(item)
        self.graph.clear()

    def get_current_layout(self):
        positions = {}
        w, h = self.width(), self.height()
        for item in self.graph.all_nodes():
            rect = item.boundingRect()
            x, y = (item.x() + rect.width() / 2) / w, (item.y() + rect.height() / 2) / h
            positions[str(id(item))] = x, y
        return positions

    def get_automatic_layout(self, root):
        return layout(self.graph, root=root)

    def apply_layout(self, positions):
        w, h = self.width(), self.height()
        #~ print('w, h:', (w, h))
        #~ margin = 20
        #~ w -= 2 * margin
        #~ h -= 2 * margin
        for item, pos in positions.items():
            rect = item.boundingRect()
            #~ print(rect)
            x, y = pos[0] * w  - rect.width() / 2, pos[1] * h - rect.height() / 2
            #~ print(item, (x, y))
            item.setPos(x, y)

    def get_interm_repr(self, root):
        nil_obj = '#atom', 'nil'
        nil_id = str(id(nil_obj))
        _graph = {}
        _visited = set()
        def make_graph(node):
            if node in _visited: return
            _visited.add(node)
            if isinstance(node, GAtom):
                _graph[str(id(node))] = '#atom', node.value
            elif isinstance(node, GCons):
                tmp = {}
                for _, nd, k, _ in self.graph.outcoming_edges(node):
                    tmp[k] = str(id(nd))
                    make_graph(nd)
                children = [tmp.get('car', nil_id), tmp.get('cdr', nil_id)]
                if nil_id in children:
                    _graph[nil_id] = nil_obj
                _graph[str(id(node))] = '#cons', children
            else:
                raise RuntimeError('unexepted node: ' + repr(node))
        make_graph(root)
        return GraphExpr(str(id(root)), _graph)


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

    def addCons(self) :
        self.scene.addObj(GCons())

    def addAtom(self, value=None) :
        self.scene.addObj(GAtom(value))

    def removeSelectedItem(self) :
        for item in self.scene.selectedItems() :
            if isinstance(item, Pointer):
                self.scene.removePointer(item)
            elif isinstance(item, (GCons, GAtom)):
                self.scene.removeObj(item)
            else:
                self.scene.removeItem(item)

    def removeDisconnected(self):
        root = self.rootArrow.root
        tree = {} if root is None else self.scene.graph.get_tree(root)
        for orphan in self.scene.graph.all_nodes().difference(tree.keys()):
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
                if self.arrow.start != endItem and isinstance(endItem, (GCons, GAtom)):
                    #~ Remove prev pointer if nedeed
                    # TODO : faire ça dans la scene
                    for oldPointer in self.scene.getEdgesFrom(self.arrow.start, self.arrow.orig):
                        self.scene.removePointer(oldPointer)

                    #~ Create new pointer
                    p = Pointer(self.arrow.start, endItem, self.arrow.orig)
                    self.scene.addPointer(p)
                    break
            self.scene.removeItem(self.arrow)
            self.arrow = None

        super().mouseReleaseEvent(mouseEvent)
