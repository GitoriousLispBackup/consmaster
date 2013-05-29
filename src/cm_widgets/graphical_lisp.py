#!/usr/bin/python3
# -*- coding: utf-8 -*-

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class DiGraph:
    def __init__(self):
        self._vertices = set()
        self._edges = {}

    def clear(self):
        self._vertices.clear()
        self._edges.clear()

    def add_vertex(self, v):
        self._vertices.add(v)

    def add_edge(self, v1, v2, key, **kwargs):
        self.add_vertex(v1)
        self.add_vertex(v2)
        self._edges.setdefault((v1, v2), {}).update({key : kwargs})

    def remove_edge(self, v1, v2, key):
        self._edges[v1, v2].pop(key)
        if not self._edges[v1, v2]:
            self._edges.pop((v1, v2))

    def remove_all_edges(self, v1, v2):
        self._edges.pop((v1, v2))            

    def remove_vertex(self, v):
        for u in self.successors(v):
            self.remove_edge(v, u)
        for u in self.predecessors(v):
            self.remove_edge(u, v)
        self._vertices.remove(v)

    def incoming_edges(self, vertex, key=None):
        for u, v in filter(lambda v: v[1] is vertex, self._edges.keys()):
            if key != None:
                yield u, v, key, self._edges[u,v][key]
            else:
                for k, data in self._edges[u,v].items():
                    yield u, v, k, data
                
    def outcoming_edges(self, vertex, key=None):
        for v, u in filter(lambda v: v[0] is vertex, self._edges.keys()):
            if key != None:
                yield v, u, key, self._edges[v,u][key]
            else:
                for k, data in self._edges[v,u].items():
                    yield v, u, k, data

    def predecessors(self, vert, key=None):
        return {u for u, v, _, _ in self.incoming_edges(vert, key)}

    def successors(self, vert, key=None):
        return {u for v, u, _, _ in self.outcoming_edges(vert, key)}
    
    def __repr__(self):
        V = repr(self._vertices)
        E = '\n'.join('   ' + repr(u) + ' -> ' + repr(v) for u, v in self._edges.keys())
        return '<digraph:\n\tvertices = ' + V + '\n\tedges = [\n' + E + ' ]\n>'



from collections import OrderedDict


def layout(G, root):
    levels = OrderedDict()
    visited = set()
    def set_dist(node=root, dst=0):
        visited.add(node)
        levels.setdefault(dst, []).append(node)
        for u, v, k, _ in sorted(G.outcoming_edges(node), key=lambda tp: tp[2]):  # car before cdr
            if v not in visited:
                set_dist(v, dst + (1 if k == 'car' else 0))
    set_dist()

    positions = {}
    h = len(levels)
    for j, nodes in levels.items():
        w = len(nodes)
        y = (j + 1) / (h + 1)
        for i, nd in enumerate(nodes):
            x = (i + 1) / (w + 1)
            positions[nd] = x, y
    
    print(levels)

    return positions

import math
from functools import reduce

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class GraphicalLispGroupWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()

        self.glisp_widget = GlispWidget(self)

        glispAddCons = QPushButton("Add Cons")
        glispAddAtom = QPushButton("Add Atom")
        glispRemove = QPushButton("Remove")
        glispCleanAll = QPushButton("Clean All")

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(glispAddCons)
        self.buttons_layout.addWidget(glispAddAtom)
        self.buttons_layout.addWidget(glispRemove)
        self.buttons_layout.addWidget(glispCleanAll)

        #~ Actions
        glispAddCons.clicked.connect(self.glisp_widget.addCons)
        glispAddAtom.clicked.connect(self.glisp_widget.addAtom)
        glispRemove.clicked.connect(self.glisp_widget.removeSelectedItem)
        glispCleanAll.clicked.connect(self.glisp_widget.removeAll)

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

    def layouting(self, root):
        positions = layout(self.graph, root=root)
        #~ print(positions.values())
        w, h = self.width(), self.height()
        #~ print('w, h:', (w, h))
        #~ margin = 20
        #~ w -= 2 * margin
        #~ h -= 2 * margin
        for item, pos in positions.items():
            rect = item.boundingRect()
            #~ print(rect)
            x, y = pos[0] * w  - rect.width(), pos[1] * h - rect.height()
            #~ print(item, (x, y))
            item.setPos(x, y)


class GlispWidget(QGraphicsView) :
    """ Widget for graphical lisp """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.arrow = None
        self.mousePos = None
        self.startItem = None
        self.startItemType = ""

        self.scene = LispScene()
        self.scene.setSceneRect(QRectF(0, 0, 600, 300))
        self.setRenderHint(QPainter.Antialiasing)

        self.scene.update()

        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        self.scene.addItem(RootArrow(None, None, self.scene))

        self.show()

    @Slot(object)
    def insert_expr(self, graph_expr):
        self.scene.reset()

        dct = {}
        for k, v in graph_expr.graph.items():
            if v[0] == '#cons':
                g = GCons()
            elif v[0] == '#atom':
                if v[1] == 'nil': continue
                g = GAtom(v[1])
            else:
                raise RuntimeError('not implemented')
            self.scene.addObj(g)
            dct[k] = g
        for k, g in dct.items():
            if isinstance(g, GCons):
                car_id, cdr_id = graph_expr.graph[k][2]
                car, cdr = dct.get(car_id), dct.get(cdr_id)
                if car: self.scene.addPointer(Pointer(g, car, 'car'))
                if cdr: self.scene.addPointer(Pointer(g, cdr, 'cdr'))
        self.scene.layouting(dct[graph_expr.root])

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

    def removeAll(self) :
        self.scene.reset()


    def mousePressEvent(self, mouseEvent):
        #~ Allows to create tmp arrows w/ right clic
        self.scene.clearSelection()
        if mouseEvent.button() == Qt.RightButton:
            pos = mouseEvent.pos()
            it = self.itemAt(pos)
            if isinstance(it, GCons) :
                self.arrow = Arrow(pos, pos, it)
                self.arrow.penColor = Qt.red
                self.startItemType = it.isCarOrCdr(pos - it.pos().toPoint())
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
                    for oldPointer in self.scene.getEdgesFrom(self.arrow.start, self.startItemType):
                        self.scene.removePointer(oldPointer)

                    #~ Create new pointer
                    p = Pointer(self.arrow.start, endItem, self.startItemType)
                    self.scene.addPointer(p)
                    break
            self.scene.removeItem(self.arrow)
            self.arrow = None

        super().mouseReleaseEvent(mouseEvent)


#~ QGraphicsItem can handle animations, could be funny
class GCons(QGraphicsItem):
    """ A graphical cons base class """

    def __init__(self, car=None, cdr=None, iden=None, parent=None, scene=None):
        super().__init__(parent, scene)
        self.setFlags(QGraphicsItem.ItemIsMovable|QGraphicsItem.ItemIsSelectable)

        self.car = car
        self.cdr = cdr

        #~ Best should be hSize=wSize/2
        self.hSize = 40
        self.wSize = 80

        self.used = ""

        self.penWidth = 2
        self.penColor = QPen(Qt.black, self.penWidth)
        self.boundingRect()

    def selectedActions(self, value) :
        if value:
            self.penColor = QPen(QColor("crimson"), self.penWidth)
        else:
            self.penColor = QPen(QColor("black"), self.penWidth)

    def boundingRect(self) :
        return QRectF (0 - self.penWidth / 2, 0 - self.penWidth / 2,
                       self.wSize + self.penWidth, self.hSize + self.penWidth)

    def paint(self, painter, option, widget=None) :
        painter.setPen(self.penColor)
        painter.drawRoundRect(0, 0, self.wSize/2-1, self.hSize)
        painter.drawRoundRect(self.wSize/2, 0, self.wSize/2, self.hSize)
        #~ Drawing / if car/cdr is Nil
        if self.car == None :
            #~ painter.drawLine(0+2, 0+2, 50-2, 50-2)
            painter.drawLine(0+2, self.hSize-2, self.wSize/2-2, 0+2)
        if self.cdr == None :
            painter.drawLine(self.wSize/2+2, self.hSize-2, self.wSize-2, 0+2)
            #~ painter.drawLine(50+2, 0+2, 100-2, 50-2)


    def itemChange(self, change, value) :
        if change == self.ItemSelectedChange:
            self.selectedActions(value)
        return super().itemChange(change, value)

    def isCarOrCdr(self, mousePos) :
        if mousePos.x() < self.wSize / 2:
            return "car"
        else :
            return "cdr"

    def mousePressEvent(self, mouseEvent) :
        self.used = self.isCarOrCdr(mouseEvent.pos())
        #~ Next line needed to force redrawn of the cons
        self.setSelected(False)
        super().mousePressEvent(mouseEvent)
        #self.setSelected(False)

    def mouseMoveEvent(self, mouseEvent):
        super().mouseMoveEvent(mouseEvent)

    def __repr__(self):
        return 'cons_' + str(id(self)) + '[' + repr(id(self.car)) + ',' + repr(id(self.cdr)) + ']'


class GAtom(QGraphicsItem):
    """ An Graphical Atom to represent a Car """

    def __init__(self, value=None, parent=None, scene=None):
        super().__init__(parent, scene)

        self.setFlags(QGraphicsItem.ItemIsMovable|QGraphicsItem.ItemIsSelectable)

        self._value = "nil"  # ??
        self.sizedBound = 0

        self.penWidth = 2
        self.pen = QPen(Qt.black, self.penWidth)

        if value is None:
            self.setValueBox()
        else:
            self.value = value

    def setValue(self, value):
        self._value = value
        self.sizedBound = 20 + len(self.value)*10
        #~ Seems to be working without this, but is asked in
        #~  documentation, as we change the bounding box
        self.prepareGeometryChange()
        #~ self.boundingRect()
        #~ self.update()

    value = property(fget=lambda self: self._value, fset=setValue)

    def selectedActions(self, value) :
        if value:
            self.pen = QPen(QColor("crimson"), self.penWidth)
        else:
            self.pen = QPen(QColor("black"), self.penWidth)

    def boundingRect(self) :
        return QRectF (0 - self.penWidth / 2, 0 - self.penWidth / 2,
                       self.sizedBound + self.penWidth, 30 + self.penWidth)

    def paint(self, painter, option, widget=None) :
        painter.setPen(self.pen)
        rect = QRectF(0, 0, self.sizedBound, 30)
        painter.drawEllipse(rect)
        painter.drawText(rect, Qt.AlignCenter, self.value)

    def itemChange(self, change, value) :
        if change == self.ItemSelectedChange :
            self.selectedActions(value)
        return super().itemChange(change, value)

    def setValueBox(self, currentName=None):
        name, ok = QInputDialog.getText(None, "Atom", "Contenu de l'atome :",
                    QLineEdit.Normal, currentName)
        # TODO: control if name is valid
        if ok and name != "":
            self.value = name

    def mouseDoubleClickEvent(self, mouseEvent) :
        self.setValueBox(self.value)

    def __repr__(self):
        return 'atom_' + repr(self.value)


class Arrow(QGraphicsLineItem):
    """Arrow
    Args:
        p1: start QPointF
        p2: end QPointF
    """

    def __init__(self, p1, p2, startItem, parent=None, scene=None):
        super().__init__(parent, scene)
        self.base = QRectF()
        self.baseSize = 6
        self.bodySize = 2
        self.headSize = 12
        self.start = startItem
        self.head = QPolygonF()
        self.penColor = Qt.black
        self.penStyle = Qt.SolidLine
        self.setLine(QLineF(p1, p2))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def boundingRect(self):
        extra = (self.pen().width() + self.headSize) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).\
               normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        # The shape is used to detect collisions and receive mouse clicks,
        # so we must set the shape accordingly with elements we added
        # to the line item : base and head
        path = super().shape()
        path.addRect(self.base)
        path.addPolygon(self.head)
        return path

    def paint(self, painter, option, widget=None):
        # We have to tell the view how to paint an arrow
        # Firstly the base, then the body and finally the head
        painter.setPen(QPen(self.penColor, self.bodySize, self.penStyle))
        painter.setBrush(self.penColor)
        body = self.line()

        # Paint the base ellipse
        self.base = QRectF(body.p1().x() - self.baseSize / 2,
                           body.p1().y() - self.baseSize / 2,
                           self.baseSize, self.baseSize)
        painter.drawEllipse(self.base)

        # Paint the body
        if body.length() == 0:
            return
        painter.drawLine(body)

        # Paint the head
        if body.length() < self.headSize:
            headSize = body.length()
        else:
            headSize = self.headSize
        angle = math.acos(body.dx() / body.length())
        if body.dy() >= 0:
            angle = (math.pi * 2.0) - angle
        v1 = body.p2() - QPointF(math.sin(angle + math.pi / 3.0) * headSize,
                                 math.cos(angle + math.pi / 3.0) * headSize)
        v2 = body.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3.0) * headSize,
                                 math.cos(angle + math.pi - math.pi / 3.0) * headSize)
        head = QPolygonF()
        for vertex in [body.p2(), v1, v2]:
            head.append(vertex)
        painter.drawPolygon(head)
        self.head = head

class RootArrow (Arrow) :
    """ Special and unique arrow to set root
        Can be open moved, and sticky when assigned
    """

    def __init__(self, position=QPointF(50, 50), rootItem=None, parent=None, scene=None):
        super().__init__(QPointF(0, 0), QPointF(50, 50), parent, scene)

        if rootItem == None :
            self.pos = QPointF(50, 50)
            self.root = None
        else :
            self.root = rootItem
            self.pos = rootItem.pos()

        self.setFlags(QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemIsMovable)
        self.penColor = QColor("steelblue")
        self.penStyle = Qt.SolidLine
        #~ Toujours dessus
        self.setZValue(200)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.penColor)
        if isinstance(self.root, GCons) :
            self.pos = self.root.pos() + QPointF(0, self.root.hSize/2)
        elif isinstance(self.root, GAtom) :
            self.pos = self.root.pos() + QPointF(0, 15)
        self.setLine(QLineF(QPointF(0,0), self.pos))
        super().paint(painter, option, widget)

    def mousePressEvent(self, mouseEvent) :
        self.pos = mouseEvent.scenePos()
        super().mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent) :
        self.pos = mouseEvent.scenePos()
        self.setLine(QLineF(QPointF(0,0), self.pos))
        super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent) :
        self.pos = mouseEvent.scenePos()
        for item in self.scene().items(mouseEvent.pos()):
            if isinstance(item, GCons) or isinstance(item, GAtom) :
                self.root = item
            else :
                self.root = None
        self.update()
        super().mouseReleaseEvent(mouseEvent)

class Pointer(Arrow):
    """Pointer.
    A Pointer is an Arrow, but linking two items, instead of 2 Points
    A Pointer is auto positionning

    The Pointer also modify items
    """

    def __init__(self, startItem, endItem, orig="", parent=None, scene=None):
        super().__init__(startItem.pos(), endItem.pos(), None, parent, scene)

        self.startItem = startItem
        self.endItem = endItem
        self.orig = orig

        # gestion des liens directs entre les objets
        if self.orig == "car":
            self.startItem.car = endItem
        elif self.orig == "cdr":
            self.startItem.cdr = endItem
        else:
            raise RuntimeError('bad link')
        self.startItem.update()

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.penColor = QColor("black")


    def paint(self, painter, option, widget=None):
        painter.setPen(self.penColor)
        #~ Set origin position
        if self.orig == "car" :
            p1 = self.startItem.scenePos() + QPointF(self.startItem.wSize/4, self.startItem.hSize/2)
        elif self.orig == "cdr":
            p1 = self.startItem.scenePos() + QPointF(self.startItem.wSize*3/4, self.startItem.hSize/2)
        else:
            print("1. problème qq part ...", self.orig)
            return
        #~ Set destination position

        if isinstance(self.endItem, GCons) :
            p2 = self.endItem.scenePos() + QPointF(0, self.startItem.hSize/2)
        elif isinstance(self.endItem, GAtom) :
            p2 = self.endItem.scenePos() + QPointF(0, 15)
        else:
            print("2. problème qq part ...", type(self.endItem))
            return

        self.setLine(QLineF(p1, p2))
        super().paint(painter, option, widget)

    def itemChange(self, change, value) :
        if change == self.ItemSelectedChange :
            self.selectedActions(value)
        return super().itemChange(change, value)

    def selectedActions(self, value) :
        if value:
            self.penStyle = Qt.DotLine
        else:
            self.penStyle = Qt.SolidLine

    def __del__(self):
        if self.orig == "car":
            self.startItem.car = None
        elif self.orig == "cdr":
            self.startItem.cdr = None
        self.startItem.update()

    def __repr__(self):
        return 'arrow_' + str(id(self))
