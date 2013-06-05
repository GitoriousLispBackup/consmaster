from pylisp import *
import pylisp.lisp_errors as lisp_errors
import pylisp.lisp as lisp
from lisp_errors import LispError, LispParseError
from lisp import _Fvals as Fvals, nil

from cm_interm_repr import GraphExpr


class Interpreter:
    counter = 0
    
    def __new__(cls, **kwargs):
        if Interpreter.counter != 0:
            raise RuntimeError('unable to create more than one interpreter')
        Interpreter.counter += 1
        return super().__new__(cls)
        
    def __init__(self, out=print):
        # print(out)
        self.out = out
        self.reset()

    def parse(self, expr):
        return lisp_parser.parse(expr, lexer=lisp_lexer)[0]

    def eval(self, expr):
        try:
            expr = self.parse(expr)
        except LispParseError as err:
            self.out(repr(err)) 
            return
        
        # print('expr :', GraphExpr.from_lsp_obj(expr))
        try:
            ret = expr.eval(self.namespace)
            self.out(repr(ret))
        except (LispError, RuntimeError) as err:
            self.out('  Error: ' + repr(err))
            return
        return ret

    def getFromEnv(self, symbol):
        return self.namespace.get(symbol)

    def reset(self):
        self.namespace = {}
        self.namespace['nil'] = nil
        Fvals.clear()

    def __del__(self):
        Interpreter.counter -= 1
