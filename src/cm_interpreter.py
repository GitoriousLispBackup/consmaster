from pylisp.lisp_lexer import lisp_lexer
from pylisp.lisp_parser import lisp_parser
from pylisp.lisp_errors import LispError, LispParseError
from pylisp.lisp import _Fvals, nil

class Interpreter:
    counter = 0
    def __new__(cls):
        if Interpreter.counter != 0:
            raise RuntimeError('unable to create more than one interpreter')
        Interpreter.counter += 1
        return super().__new__(cls)
    def __init__(self):
        self.namespace = {}
        self.namespace['nil'] = nil
        _Fvals.clear()
    def eval(self, expr):
        expr = lisp_parser.parse(expr, lexer=lisp_lexer)[0]
        return expr.eval(self.namespace)
    def getFromEnv(self, symbol):
        return self.namespace.get(symbol)
    def __del__(self):
        Interpreter.counter -= 1

