from pyrser import grammar, meta
import sys


class Parser(grammar.Grammar):
    entry = "evalExpr"
    grammar = """
    evalExpr = [ [ expr:e #print_expr(e) ]+ eof ]
    expr = [ [ num:n #init_num(_,n) | [ '(' expr:s #parenthesis1(_,s) ')' ] ] [ [ '*' | '+' | '-' | '/' | '%']:o #add_op(_,o) [ [ '+' | '-']:s #add_sign(_,s) ]* [ num:m #add_num(_,m) | [ '(' expr:s #parenthesis2(_,s) ')' ] ] ]* ]
    """


@meta.hook(Parser)
def parenthesis1(self, ast, arg):
    print(">>>", self.value(arg))
    calc(arg.values)
    ast.values = [arg.values[0]]
    return True


@meta.hook(Parser)
def parenthesis2(self, ast, arg):
    print(">>>>", self.value(arg))
    calc(arg.values)
    ast.values.append(arg.values[0])
    return True


@meta.hook(Parser)
def init_num(self, ast, arg):
    ast.values = [self.value(arg)]
    return True


@meta.hook(Parser)
def add_sign(self, ast, arg):
    if self.value(arg) == '-':
        if hasattr(ast, 'sign'):
            ast.sign = -ast.sign
        else:
            ast.sign = -1
    return True


@meta.hook(Parser)
def add_num(self, ast, arg):
    value = int(self.value(arg))
    if hasattr(ast, 'sign'):
        value *= ast.sign
        delattr(ast, 'sign')
    ast.values.append(str(value))
    return True


@meta.hook(Parser)
def add_op(self, ast, arg):
    ast.values.append(self.value(arg))
    return True


# noinspection PyUnusedLocal
@meta.hook(Parser)
def print_expr(self, arg):
    tab = arg.values
    calc(tab)
    print(tab[0])
    return True


def calc(tab):
    print(str(tab))
    while len(tab) > 1:
        index = 0
        if len(tab) > 3 and (tab[3] == '*' or tab[3] == '/' or tab[3] == '%') and (tab[1] == '+' or tab[1] == '-'):
            index = 2

        value = int(tab[index])
        result = {
            '*': lambda x: value * x,
            '+': lambda x: value + x,
            '-': lambda x: value - x,
            '/': lambda x: value // x,
            '%': lambda x: value % x
        }[tab[index + 1]](int(tab[index + 2]))
        tab[index] = str(result)
        tab.pop(index + 1)
        tab.pop(index + 1)

parser = Parser()
parser.parse_file(sys.argv[1])
