#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter
import pprint


import pylisp.lisp as lisp
from lisp import Cons, consp, atom
from pylisp import lisp_lexer, lisp_parser


class GraphExpr:
    """
    Intermediate representation for a lisp expression.

    s-expr are re presented by root element and adjacent matrix,
    like this :
    'root': "140501648984400",
    'graph': {
           '140501648983464': ['#atom', '1'],
           '140501648983608': ['#cons',
                               ['140501648984184', '140501754739024']],
           '140501648983752': ['#cons',
                               ['140501648983968', '140501648983608']],
           '140501648983968': ['#atom', '2'],
           '140501648984184': ['#atom', '3'],
           '140501648984400': ['#cons',
                               ['140501648983464', '140501648983752']],
           '140501754739024': ['#atom', 'nil'] }

    Convenience functions for converting internal lisp expression to intermediate
    representation and vice versa are provided.

    There is also some interesting functions on lisp s-expressions :
    compare if two expr are equivalent, if they are isomorphic, etc.
    """

    tag = itemgetter(0)
    value = itemgetter(1)

    def __init__(self, root, graph, **kwargs):
        self.root = root
        self.graph = graph
        # add additionnals optional attributes (like layout)
        self.__dict__.update(**kwargs)

    def to_lsp_obj(self):
        """
        Convert intermediate representation to a internal lisp object.
        """
        visited = {}

        def rec_build(uid):
            if uid in visited: return visited[uid]
            internal = self.graph[uid]
            if GraphExpr.tag(internal) == '#cons':
                id_car, id_cdr = GraphExpr.value(internal)
                obj = Cons(rec_build(id_car), rec_build(id_cdr))
            elif GraphExpr.tag(internal) == '#atom':
                obj = lisp_parser.parse(GraphExpr.value(internal), lexer=lisp_lexer)[0]  # bof
            else:
                raise RuntimeError('Unkown value ' + repr(obj) + ' in tree')
            visited[uid] = obj
            return obj
        return rec_build(self.root)

    @staticmethod
    def from_lsp_obj(obj):
        """
        Get intermediate representation from a lisp object.
        """
        visited = {}

        def rec_build(obj):
            uid = str(id(obj))
            if uid not in visited:
                if consp(obj):
                    visited[uid] = '#cons', [str(id(obj.car)), str(id(obj.cdr))]
                    if str(id(obj.car)) not in visited:
                        rec_build(obj.car)
                    if str(id(obj.cdr)) not in visited:
                        rec_build(obj.cdr)
                elif atom(obj):
                    visited[uid] = '#atom', repr(obj)
                else:
                    raise RuntimeError('Unkown value ' + repr(obj) + ' in expr')
            return uid
        return GraphExpr(rec_build(obj), visited)

    def _cmp(self, other, cmp_atom):
        """
        Compare two expressions, by using cmp_atom()
        comparizon function.
        """
        if self is other: return True
        visited = {}

        def walk(id1, id2):
            node1, node2 = self.graph[id1], other.graph[id2]
            t1, t2 = GraphExpr.tag(node1), GraphExpr.tag(node2)
            if t1 != t2:
                return False
            elif t1 == '#atom':
                return cmp_atom(GraphExpr.value(node1), GraphExpr.value(node2))
            elif t1 == '#cons':
                if id1 in visited:
                    return id2 == visited[id1]
                else:
                    visited[id1] = id2
                    return all(walk(_id1, _id2) for _id1, _id2 in zip(GraphExpr.value(node1), GraphExpr.value(node2)))
            else:
                raise RuntimeError('Unkown value in tree')
        return walk(self.root, other.root)

    def isomorphic_to(self, other):
        """
        return True if two lisp expressions are structurally
        equivalent (isomorphic), else return False.
        """
        return self._cmp(other, lambda a, b: True)

    def __eq__(self, other):
        """
        return True if two lisp expressions are equivalent,
        else return False.
        """
        return self._cmp(other, str.__eq__)

    def depth(self):
        """
        Get the depth of an lisp expression.
        """
        visited = {}

        def walk(uid, cur):
            nd = self.graph[uid]
            if GraphExpr.tag(nd) == '#atom':
                return cur
            elif GraphExpr.tag(nd) == '#cons':
                if uid in visited:
                    return visited[uid]
                visited[uid] = cur
                car_id, cdr_id = GraphExpr.value(nd)
                return max(walk(car_id, cur + 1), walk(cdr_id, cur))
        return walk(self.root, 0)

    def circular(self):
        """
        Check circularity.
        """
        visited = set()

        def walk(uid):
            nd = self.graph[uid]
            if GraphExpr.tag(nd) == '#cons':
                if uid in visited:
                    return True
                visited.add(uid)
                car_id, cdr_id = GraphExpr.value(nd)
                return walk(car_id) or walk(cdr_id)
        return walk(self.root)

    def proper(self):
        """
        Check if all conses objects have a list cdr.
        """
        visited = set()

        def walk(uid, box=None):
            nd = self.graph[uid]
            if GraphExpr.tag(nd) == '#cons':
                if uid in visited:
                    return True
                visited.add(uid)
                car_id, cdr_id = GraphExpr.value(nd)
                return walk(car_id, 'car') and walk(cdr_id, 'cdr')
            elif GraphExpr.tag(nd) == '#atom':
                return not (box == 'cdr' and GraphExpr.value(nd) != 'nil')
        return walk(self.root)

    def atoms(self):
        """
        Get atoms list, in traversal order (a single atom
        can appear twice or more).
        """
        visited = set()

        def walk(uid, acc):
            node = self.graph[uid]
            tag = GraphExpr.tag(node)
            if tag == '#atom':
                acc.append(GraphExpr.value(node))
            elif tag == '#cons':
                if uid not in visited:
                    visited.add(uid)
                    car, cdr = GraphExpr.value(node)
                    walk(car, acc)
                    walk(cdr, acc)
            else:
                raise RuntimeError('Unkown value in tree')
        lst = []
        walk(self.root, lst)
        return lst

    def __str__(self):
        return repr(self.to_lsp_obj())

    def __repr__(self):
        return '< root: ' + repr(self.root) + ';\n  graph:\n' + pprint.pformat(self.graph, indent=2) + ' >'


from math import log

def lisp_expr_level(depth, cdrType):
    return int(log(depth ** 2.5)) + 3 * cdrType

def interm_level(interm):
    if expr.circular():
        cdrType = 2
    elif not expr.proper():
        cdrType = 1
    else:
        cdrType = 0
    return lisp_expr_level(expr.depth(), cdrType)
