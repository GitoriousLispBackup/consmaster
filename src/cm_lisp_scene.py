#!/usr/bin/python3
# -*- coding: utf-8 -*-

from cm_lisp_obj import *
from cm_graph import DiGraph, layout
from cm_interm_repr import GraphExpr
from operator import itemgetter

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    print ("Error: This program needs PySide module.", file=sys.stderr)
    sys.exit(1)


class LispScene(QGraphicsScene):
    """
    Scene manager. Inherits QGraphicsScene, and use
    a multi-edge directed graph to store the lisp objects,
    in order to add and remove them easily into the scene. 
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = DiGraph()

    def addObj(self, obj):
        """
        Add lisp object into the scene.
        """
        # TODO: ajouter l'objet à une place libre
        self.graph.add_vertex(obj)
        self.addItem(obj)

    def addPointer(self, pointer):
        """
        Add pointer from a lisp object to another
        lisp object, and manage old pointers and
        internal objects references.
        """
        for oldPointer in self.getEdgesFrom(pointer.startItem, pointer.orig):
            self.removePointer(oldPointer)
        self.graph.add_edge(pointer.startItem, pointer.endItem, key=pointer.orig, arrow=pointer)
        self.addItem(pointer)
        setattr(pointer.startItem, pointer.orig, pointer.endItem)
        pointer.startItem.update()

    def removeObj(self, obj):
        """
        Remove a lisp object from scene, and manage
        connected objects.
        """
        all_edges = [data['arrow'] for u, v, k, data in self.graph.outcoming_edges(obj)]
        all_edges += [data['arrow'] for u, v, k, data in self.graph.incoming_edges(obj)]

        for arrow in set(all_edges):
            self.removePointer(arrow)
        self.graph.remove_vertex(obj)
        self.removeItem(obj)

    def removePointer(self, pointer):
        """
        Remove a pointer object from scene, and manage
        connected objects.
        """
        self.graph.remove_edge(pointer.startItem, pointer.endItem, pointer.orig)
        self.removeItem(pointer)
        setattr(pointer.startItem, pointer.orig, None)
        pointer.startItem.update()

    def getEdgesFrom(self, vertex, key=None):
        # WARNING : dans un sens seulement
        return [data['arrow'] for u, v, k, data in self.graph.outcoming_edges(vertex, key)]

    def get_tree(self, root):
        """
        Return objects connected to the root argument
        in adjacent matrix.
        """
        _graph = {}

        def make_graph(v):
            if v in _graph: return
            _graph[v] = [u for _, u, k, _ in sorted(self.graph.outcoming_edges(v), key=itemgetter(2))]
            for u in _graph[v]:
                make_graph(u)
        make_graph(root)
        return _graph

    def reset(self):
        """
        Reset the scene.
        """
        for item in self.items():
            self.removeItem(item)
        self.graph.clear()

    def getCurrentLayout(self):
        """
        Get current scene objects layout, in percents of
        width an height.
        """
        positions = {}
        w, h = self.width(), self.height()
        for item in self.graph.all_nodes():
            rect = item.boundingRect()
            x, y = (item.x() + rect.width() / 2) / w, (item.y() + rect.height() / 2) / h
            positions[item] = x, y
        return positions

    def getAutoLayout(self, root):
        """
        Call layout() function (in cm_graph) to get
        automatic layout of the graph expression
        connected to the root.
        """
        return layout(self.graph, root=root)

    def applyLayout(self, positions):
        """
        Apply the argument layout to the scene objects.
        """
        w, h = self.width(), self.height()
        for item, pos in positions.items():
            rect = item.boundingRect()
            x, y = pos[0] * w - rect.width() / 2, pos[1] * h - rect.height() / 2
            item.setPos(x, y)

    def getIntermRepr(self, root):
        """
        Return lisp intermediate representation from the
        connected lisp objects to root.
        """
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
