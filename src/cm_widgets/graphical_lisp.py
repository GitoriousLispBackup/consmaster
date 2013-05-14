#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print >> sys.stderr, "Error:", "This program needs PySide module."
    sys.exit(1)

class GlispWidget(QGraphicsView) :
    """ Widget for graphical lisp """

    def __init__(self, parent=None):
        super(GlispWidget, self).__init__(parent)

        #~ Contient la repr glisp
        self.references = []

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 400, 300))

        self.scene.update()

        self.setScene(self.scene)
        self.setAlignment(Qt.AlignLeft|Qt.AlignTop)

        self.addCons()
        self.show()

    def addCons(self) :
        g = GCons()
        g.car.setCar("a")
        g.cdr.setCdr("b")
        #~ print(g.car.value)
        #~ print(g.cdr.value)
        self.scene.addItem(g)
        pass

    def removeCons(self) :
        pass

#~ QGraphicsItem can handle animations, could be funny
class GCons(QGraphicsItem):
    """ A graphical cons base class """

    def __init__(self, carValue=None, cdrValue=None, parent=None, scene=None):
        super(GCons, self).__init__(parent, scene)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.penWidth = 2
        self.boundingRect()

        self.car = GCar()
        self.car.setParentItem(self)
        self.cdr = GCdr()
        self.cdr.setParentItem(self)

    def boundingRect(self) :
        return QRectF (0 - self.penWidth / 2, 0 - self.penWidth / 2,
                       100 + self.penWidth, 50 + self.penWidth)

    def paint(self, painter, option, widget=None) :
        painter.setPen(QPen(Qt.black, self.penWidth))
        painter.drawRoundRect(0, 0, 50, 50)
        painter.drawRoundRect(50, 0, 50, 50)

    #~ TODO: Définir la position de départ, layouting
    def setPosition(self):
        pass

    #~ TODO: Pour le référencement ?
    def identify(self) :
        return self.id(self), self.id(self.car), self.id(self.cdr)

class GCar(QGraphicsRectItem) :
    """ Car part of a gCons """

    def __init__(self, penWidth=1, parent=None, *args, **kwargs):
        super(GCar, self).__init__(parent)
        self.penWidth = 1
        self.value = "nil"

    def setCar(self, car) :
        self.value = car
        #~ Need Signal

    def boundingRect(self) :
        return QRectF (0 - self.penWidth / 2, 0 - self.penWidth / 2,
                       50 + self.penWidth, 50 + self.penWidth)

class GCdr(QGraphicsRectItem) :
    """ Cdr part of a gCons """

    def __init__(self, penWidth=1, parent=None, *args, **kwargs):
        super(GCdr, self).__init__(parent)
        self.penWidth = 1
        self.value = "nil"

    def setCdr(self, cdr) :
        self.value = cdr
        #~ Need Signal

    def boundingRect(self) :
        return QRectF (50 - self.penWidth / 2, 0 - self.penWidth / 2,
                       50 + self.penWidth, 50 + self.penWidth)

#~ Honteusement plagié temporairement
class Arrow(QGraphicsLineItem):
    """Arrow.

    An Arrow serves as drawing for Pointer.
    An arrow is basically linking a start point and an end point.
    The body is made of a line between those points.
    The base with a little ellipse.
    The head with a little triangle.

    Args:
        p1: start QPointF
        p2: end QPointF
    """

    def __init__(self, p1, p2, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)
        self.base = QRectF()
        self.baseSize = 6
        self.bodySize = 2
        self.headSize = 12
        self.head = QPolygonF()
        self.penColor = Qt.black
        self.setLine(QLineF(p1, p2))
        # Should we make arrows selectable ?
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def boundingRect(self):
        # The boundingRect tells the view if the item needs to be redrawn,
        # so we must add to it the size of the elements we added to the
        # line item : base and head
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

    A Pointer is an Arrow, but linking two items.
    It knows it's start and end items so it can morph while they move.

    Args:
        startItem: A PointerAble QGraphicsRectItem
        endItem: A ReferenceAble QGraphicsRectItem
    """

    def __init__(self, startItem, endItem, parent=None, scene=None):
        self.startItem = startItem
        self.endItem = endItem
        self.p1 = startItem.scenePos() + QPointF(100, 50)
        self.p2 = endItem.scenePos()
        super(Pointer, self).__init__(self.p1, self.p2, parent, scene)

    def paint(self, painter, option, widget=None):
        self.p1 = self.startItem.scenePos() + QPointF(75, 25)
        self.p2 = self.endItem.scenePos() + QPointF(0, 25)
        self.setLine(QLineF(self.p1, self.p2))
        super(Pointer, self).paint(painter, option, widget)
