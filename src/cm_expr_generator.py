#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pylisp import *
import pylisp.lisp as lisp
from lisp import Cons, Symbol

import random
import string

_default_candidates = string.ascii_letters #  + string.digits


def gen_with_doublons(candidates=_default_candidates):
    while True:
        yield random.choice(candidates)

def gen_with_no_doublons(candidates=_default_candidates):
    for sym in random.shuffle(candidates):
        yield sym


# allow lopps ?
def exp_generator(max_depth=1, max_len=4, proper=1., sym_gen=gen_with_doublons()):
    """
    générateur aléatoire d'expressions lisp
    max_depth:   profondeur de la liste
    max_len: longueur maximale d'une liste/sous-liste
    proper:  probabilité d'avoir seulement des listes "propres" (0.5 ou  1.0)
    sym_gen: générateur de symboles/valeurs atomiques
    """
    def rec_build(_depth, _len):
        if _depth < max_depth and random.random() < 0.45:
            car = rec_build(_depth + 1, 0)
        else:
            car = 'nil' if random.random() < 0.05 else next(sym_gen)
        if random.random() > (_len / max_len):
            cdr = rec_build(_depth, _len + 1)
        else:
            cdr = 'nil' if random.random() < proper else next(sym_gen)
        return car, cdr
    def get_lisp_obj(expr):
        if isinstance(expr, tuple):
            return Cons(get_lisp_obj(expr[0]), get_lisp_obj(expr[1]))
        else:
            return Symbol(expr)     
    return get_lisp_obj(rec_build(1, 0))

# testing
if __name__ == '__main__':
    [(1, 1.), (1, 0.5), (2, 1.), (2, 0.5)]
    for depth, proper in [(1, 1.), (1, 0.5), (2, 1.), (2, 0.5)]:
        print('get for defaul legth, depth =', depth, 'proper =', proper)
        for i in range(20):
            expr = exp_generator(depth, proper=proper)
            print('\t', expr)
            
