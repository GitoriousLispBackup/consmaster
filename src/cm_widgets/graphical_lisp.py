#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math

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
        glispRemove.clicked.connect(self.glisp_widget.removeItem)
        glispCleanAll.clicked.connect(self.glisp_widget.removeAll)

        self.layout.addWidget(self.glisp_widget)
        self.layout.addLayout(self.buttons_layout)
        self.setLayout(self.layout)


class GlispWidget(QGraphicsView) :
    """ Widget for graphical lisp """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.arrow = None
        self.mousePos = None
        self.startItem = None
        self.startItemType = ""

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 400, 300))

        self.scene.update()

        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        self.show()

    def addCons(self, car=None, cdr=None) :
        g = GCons(car, cdr)
        #~ a = None
        #~ arrow = None
        #~ if g.car != None :
            #~ a = self.addAtom(g.car)
            #~ arrow = self.addArrow(g, a, "car")
        self.scene.addItem(g)

    def removeItem(self) :
        for item in self.scene.selectedItems() :
            self.scene.removeItem(item)
            if isinstance(item, Pointer) :
                item.delete()
            elif isinstance(item, GCons) :
                #~ Remove all pointer from it
                for orig in ["car", "cdr"] :
                    pointer = self.findPointerFrom(item, orig)
                    if pointer != None :
                        pointer.deleteLinks()
                        self.scene.removeItem(pointer)
                #~ Remove all pointer to it
                for orig in ["car", "cdr"] :
                    list = self.findPointersTo(item)
                    if list != [] :
                        for x in list :
                            x.deleteLinks()
                            self.scene.removeItem(x)

    def addAtom(self, value=None) :
        a = GAtom(value)
        self.scene.addItem(a)
        # NOTICE: For arrow creation
        return a

    def removeAll(self) :
        for item in self.items() :
            self.scene.removeItem(item)

    def findPointerFrom(self, gcons, orig) :
        """ Return the pointer associated w/ a car or a cons """
        for item in self.scene.items() :
            if isinstance(item, Pointer) :
                if item.startItem == gcons :
                    if item.orig == orig :
                        return item

    def findPointersTo(self, gcons) :
        """ Return who pointing here """
        list = []
        for item in self.scene.items() :
            if isinstance(item, Pointer) :
                if item.endItem == gcons :
                    list.append(item)
        return list

    #~ def addArrow(self, o1, o2, orig) :
        #~ p = Pointer(o1, o2)
        #~ self.scene.addItem(p)
        #~ return p

    #~ TODO
    #~ def autoArrow(self) :
        #~ for item in self.items() :
            #~ if isinstance(item, GCons) :
                #~ if self.references[item][0] != None :
                    #~ if self.references[item][0] in self.references.values() :
                        #~ self.addArrow(item, self.references[self.references[item][0]])

    #~ TODO
    #~ def autoArrowClean(self) :
        #~ for item in self.scene.items() :
            #~ if isinstance(item, Pointer) :
                #~ if item.startItem == None or item.endItem == None :
                    #~ self.scene.removeItem(item)

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
        if (self.arrow != None) :
            newLine = QLineF(self.arrow.line().p1(), mouseEvent.pos())
            self.arrow.setLine(newLine)

        super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        #~ Should also test if already linked

        if self.arrow != None :
            for endItem in self.items(mouseEvent.pos()):
                if (isinstance(endItem, GCons) and self.arrow.start != endItem) or isinstance(endItem, GAtom) :
                    #~ Remove prev pointer if nedeed
                    oldPointer = self.findPointerFrom(self.arrow.start, self.startItemType)
                    if oldPointer != None :
                        oldPointer.deleteLinks()
                        self.scene.removeItem(oldPointer)

                    #~ Create new pointer
                    p = Pointer(self.arrow.start, endItem, self.startItemType)
                    self.scene.addItem(p)
                    break
            self.scene.removeItem(self.arrow)
            self.arrow = None
        super().mouseReleaseEvent(mouseEvent)


#~ QGraphicsItem can handle animations, could be funny
class GCons(QGraphicsItem):
    """ A graphical cons base class """

    def __init__(self, car=None, cdr=None, iden=None, parent=None, scene=None):
        super().__init__(parent, scene)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self._car = car
        self._cdr = cdr

        self.used = ""

        self.penWidth = 2
        self.penCar = QPen(Qt.black, self.penWidth)
        self.penCdr = QPen(Qt.black, self.penWidth)
        self.boundingRect()

    def setCar(self, car):
        self._car = car

    def setCdr(self, cdr):
        self._cdr = cdr

    def selectedActions(self, value) :
        if value :
            if self.used == "car" :
                self.setColor("green", "black")
            else :
                self.setColor("black", "green")
        else : self.setColor("black", "black")

    def setColor(self, colorCar="black", colorCdr="black") :
        self.penCar = QPen(QColor(colorCar), self.penWidth)
        self.penCdr = QPen(QColor(colorCdr), self.penWidth)

    def boundingRect(self) :
        return QRectF (0 - self.penWidth / 2, 0 - self.penWidth / 2,
                       100 + self.penWidth, 50 + self.penWidth)

    def paint(self, painter, option, widget=None) :
        painter.setPen(self.penCar)
        painter.drawRoundRect(0, 0, 50-1, 50)
        painter.setPen(self.penCdr)
        painter.drawRoundRect(50, 0, 50, 50)
        if self.car == None :
            painter.setPen(self.penCar)
            painter.drawLine(0+2, 0+2, 50-2, 50-2)
            painter.drawLine(0+2, 50-2, 50-2, 0+2)
        if self.cdr == None :
            painter.setPen(self.penCdr)
            painter.drawLine(50+2, 50-2, 100-2, 0+2)
            painter.drawLine(50+2, 0+2, 100-2, 50-2)

    #~ TODO: Définir la position de départ, layouting
    def setPosition(self):
        pass

    def itemChange(self, change, value) :
        if change == self.ItemSelectedChange:
            self.selectedActions(value)
        return super().itemChange(change, value)

    def isCarOrCdr(self, mousePos) :
        if mousePos.x() < 50 :
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

    car = property(fget=lambda self: self._car, fset=setCar)
    cdr = property(fget=lambda self: self._cdr, fset=setCdr)


class GAtom(QGraphicsItem):
    """ An Graphical Atom to represent a Car """

    def __init__(self, value="nil", parent=None, scene=None):
        super().__init__(parent, scene)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self._value = "nil"
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
        if value :
            self.pen = QPen(QColor("green"), self.penWidth)
        else : self.pen = QPen(QColor("black"), self.penWidth)

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

    def setValueBox(self, currentName=None) :
        name, ok = QInputDialog.getText(None, "Atom", "Contenu de l'atome :",
                    QLineEdit.Normal, currentName)
        #~ No control for now, needs atom list
        #~ if ok and name != "" and name in self.symbols:
            #~ q = QMessageBox(self.parent)
            #~ q.setWindowTitle("Erreur lisp")
            #~ q.setText("Un symbole avec ce nom existe.")
            #~ q.setIconPixmap(QPixmap("icons/user-busy.png"))
            #~ q.show()
        #~ elif ok and name != "":
            #~ return name
        if ok and name != "":
            self.value = name

    def mouseDoubleClickEvent(self, mouseEvent) :
        self.setValueBox(self.value)

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
        path = super(Arrow, self).shape()
        path.addRect(self.base)
        path.addPolygon(self.head)
        return path

    def paint(self, painter, option, widget=None):
        # We have to tell the view how to paint an arrow
        # Firstly the base, then the body and finally the head
        painter.setPen(QPen(self.penColor, self.bodySize, Qt.SolidLine))
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


class Pointer(Arrow):
    """Pointer.
    A Pointer is an Arrow, but linking two items, instead of 2 Points
    A Pointer is auto positionning

    The Pointer also modify items
    """

    def __init__(self, startItem, endItem, orig="", parent=None, scene=None):
        super().__init__(startItem.pos(), endItem.pos(), orig,  parent, scene)

        self.startItem = startItem
        self.endItem = endItem
        self.orig = orig

        if self.orig == "car" :
            self.startItem.car = endItem
        else :
            self.startItem.cdr = endItem
        self.startItem.update()

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.penColor = QColor("black")

    def paint(self, painter, option, widget=None):
        painter.setPen(self.penColor)
        #self.p1 = self.startItem.scenePos() + QPointF(75, 25)
        if self.orig == "car" :
            p1 = self.startItem.scenePos() + QPointF(25, 25)
        elif self.orig == "cdr":
            p1 = self.startItem.scenePos() + QPointF(75, 25)
        else : print("problème qq part ...")
        if isinstance(self.endItem, GCons) :
            p2 = self.endItem.scenePos() + QPointF(0, 25)
        elif isinstance(self.endItem, GAtom) :
            p2 = self.endItem.scenePos() + QPointF(0, 15)
        self.setLine(QLineF(p1, p2))
        super().paint(painter, option, widget)

    def itemChange(self, change, value) :
        if change == self.ItemSelectedChange :
            self.selectedActions(value)
        return super().itemChange(change, value)

    def selectedActions(self, value) :
        if value :
            self.penColor = QColor("green")
        else : self.penColor = QColor("black")

    def deleteLinks(self) :
        if self.orig == "car" :
            self.startItem.car = None
        else :
            self.startItem.cdr = None
        self.startItem.update()
