#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter

from pylisp import *
import pylisp.lisp as lisp
from lisp import Cons, consp, atom
from pprint import pformat


class GraphExpr:
    tag = itemgetter(0)
    value = itemgetter(1)
    
    def __init__(self, root, graph, **kwargs):
        self.root = root
        self.graph = graph
        self.__dict__.update(**kwargs)
    
    def to_lsp_obj(self):
        visited = {}
        def rec_build(uid):
            if uid in visited: return visited[uid]
            internal = self.graph[uid]
            if GraphExpr.tag(internal) == '#cons':
                id_car, id_cdr = GraphExpr.value(internal)
                obj = Cons(rec_build(id_car), rec_build(id_cdr))
            elif GraphExpr.tag(internal) == '#atom':
                obj = lisp_parser.parse(GraphExpr.value(internal), lexer=lisp_lexer)[0] # bof
            else:
                raise RuntimeError('Unkown value in tree')
            visited[uid] = obj
            return obj
        return rec_build(self.root)

    @staticmethod
    def from_lsp_obj(obj):
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
                    raise RuntimeError('Unkown value in expr')
            return uid
        return GraphExpr(rec_build(obj), visited)

    def _cmp(self, other, cmp_atom):
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
        return self._cmp(other, lambda a, b: True)

    def __eq__(self, other):
        return self._cmp(other, str.__eq__)

    def __repr__(self):
        return '< root: ' + repr(self.root) + ';\n  graph:\n' + pformat(self.graph, indent=2) + ' >'
