from pylisp import *

class Interpreter:
    counter = 0
    def __new__(cls):
        if Interpreter.counter != 0:
            raise RuntimeError('unable to create more than one interpreter')
        Interpreter.counter += 1
        return super().__new__(cls)
    def __init__(self, out=print):
        self.out = out
        self.reset()
    def eval(self, expr):
        try:
            expr = lisp_parser.parse(expr, lexer=lisp_lexer)[0]
        except LispParseError as err:
            self.out(repr(err))
            return
        try:
            ret = expr.eval(self.namespace)
            self.out(ret)
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

