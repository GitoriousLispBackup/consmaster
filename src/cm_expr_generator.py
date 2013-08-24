#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import string

import pylisp.lisp as lisp
from lisp import Cons, Symbol


# max_depth, max_len, proper
_cm_levels = {
    0: (1, 4, 1.),
    1: (2, 5, 1.),
    2: (3, 4, 1.),
    3: (1, 5, 0.4),
    4: (2, 4, 0.5),
    5: (3, 4, 0.7),
    6: (4, 5, 0.65)
}


_default_candidates = string.ascii_letters  # + string.digits


def gen_with_duplicates(candidates=_default_candidates):
    """
    symbol generator (with duplicates) : yield random choice in candidates
    """
    while 1: yield random.choice(candidates)

def gen_without_duplicates(candidates=_default_candidates):
    """
    symbol generator (without duplicates) : yield random choice in candidates;
    raise StopIteration exception if no more candidate available."""
    for sym in random.shuffle(candidates):
        yield sym


# allow lopps ?
def exp_generator(level, sym_gen=gen_with_duplicates()):
    """
    générateur aléatoire d'expressions lisp
    level: niveau requis
    sym_gen:  générateur de symboles/valeurs atomiques
    """
    
    max_depth, max_len, proper = _cm_levels[level]
    
    def rec_build(_depth, _len):
        # set car value
        if _depth < max_depth and random.random() < 0.4:
            car = rec_build(_depth + 1, 0)
        else:
            car = 'nil' if (level > 2 and random.random() < 0.05) else next(sym_gen)
        # set cdr value
        if random.random() < (1 - _len / max_len) ** 2:
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


def level_expr_gen(level=None):
    """
    Expression generator for defined level.
    """
    maxi = max(_cm_levels.keys())
    if level > maxi: level = maxi
    while True:
        # TODO: add test on expression level
        yield exp_generator(level)

# testing
if __name__ == '__main__':
    for level in range(len(_cm_levels)):
        print('get for level =', level)
        for i in range(20):
            expr = exp_generator(level)
            print('\t', expr)
