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
        self._edges.setdefault((v1, v2), {}).update({key: kwargs})

    def remove_edge(self, v1, v2, key):
        self._edges[v1, v2].pop(key)
        if not self._edges[v1, v2]:  # if no edge remained
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
        if vertex not in self._vertices:
            raise RuntimeError(repr(vertex) + ' not in graph')
        for u, v in filter(lambda v: v[1] is vertex, self._edges.keys()):
            edges = self._edges[u, v]
            if key != None:
                if key in edges:
                    yield u, v, key, edges[key]
            else:
                for k, data in edges.items():
                    yield u, v, k, data

    def outcoming_edges(self, vertex, key=None):
        if vertex not in self._vertices:
            raise RuntimeError(repr(vertex) + ' not in graph')
        for v, u in filter(lambda v: v[0] is vertex, self._edges.keys()):
            edges = self._edges[v, u]
            if key != None:
                if key in edges:
                    yield v, u, key, edges[key]
            else:
                for k, data in edges.items():
                    yield v, u, k, data

    def predecessors(self, vert, key=None):
        return {u for u, v, _, _ in self.incoming_edges(vert, key)}

    def successors(self, vert, key=None):
        return {u for v, u, _, _ in self.outcoming_edges(vert, key)}

    def all_nodes(self):
        return self._vertices.copy()

    def __repr__(self):
        V = repr(self._vertices)
        E = '\n'.join('   ' + repr(u) + ' -> ' + repr(v) for u, v in self._edges.keys())
        return '<digraph:\n\tvertices = ' + V + '\n\tedges = [\n' + E + ' ]\n>'


from collections import OrderedDict


def layout(G, root):
    """
    Automatically set layout for the directed graph
    connected to root elem (this is adapted for layouting
    tree expression, but a bit inconsistent because there're
    no valid position for remaining objets).
    """

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

    # print(levels)

    return positions
