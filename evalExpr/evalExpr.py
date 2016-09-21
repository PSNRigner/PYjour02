from pyrser import grammar, meta
import sys

v = {}


class Parser(grammar.Grammar):
    entry = "evalExpr"
    grammar = """
    evalExpr =  [
                    [
                        expr:e #print_expr(_,e)
                    ]+
                    eof
                ]

    expr =  [
                [
                    id:v '=' #init_var(_,v)
                ]?
                [
                    [
                        '+' | '-'
                    ]:s #add_sign(_,s)
                ]*
                [
                    num:n #init_num(_,n) |
                    id:i #add_var(_,i) |
                    [
                        '(' expr:s #parenthesis1(_,s) ')'
                    ]
                ]
                [
                    [
                    '*' | '+' | '-' | '/' | '%'
                    ]:o #add_op(_,o)
                    [
                        [
                            '+' | '-'
                        ]:s #add_sign(_,s)
                    ]*
                    [
                        num:m #add_num(_,m) |
                        id:i #add_var(_,i) |
                        [
                            '(' expr:s #parenthesis2(_,s) ')'
                        ]
                    ]
                ]*
            ]
    """


@meta.hook(Parser)
def init_var(self, ast, arg):
    ast.var = self.value(arg)
    return True


# noinspection PyUnusedLocal
@meta.hook(Parser)
def parenthesis1(self, ast, arg):
    calc(arg.val)
    ast.val = [arg.val[0]]
    return True


# noinspection PyUnusedLocal
@meta.hook(Parser)
def parenthesis2(self, ast, arg):
    calc(arg.val)
    ast.val.append(arg.val[0])
    return True


@meta.hook(Parser)
def init_num(self, ast, arg):
    value = int(self.value(arg))
    if hasattr(ast, 'sign'):
        value *= ast.sign
        delattr(ast, 'sign')
    ast.val = [str(value)]
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
    ast.val.append(str(value))
    return True


@meta.hook(Parser)
def add_op(self, ast, arg):
    if not hasattr(ast, 'val'):
        ast.val = []
    ast.val.append(self.value(arg))
    return True


@meta.hook(Parser)
def add_var(self, ast, arg):
    value = self.value(arg)
    if not hasattr(ast, 'val'):
        ast.val = []
    if hasattr(ast, 'sign'):
        if ast.sign == -1:
            value = "-" + value
        delattr(ast, 'sign')
    ast.val.append(value)
    return True


# noinspection PyUnusedLocal
@meta.hook(Parser)
def print_expr(self, ast, arg):
    tab = arg.val
    calc(tab)
    print(tab[0])
    if hasattr(arg, 'var'):
        v[arg.var] = tab[0]
    return True


def calc(tab):
    while len(tab) > 1:
        index = 0
        if len(tab) > 3 and (tab[3] == '*' or tab[3] == '/' or tab[3] == '%') and (tab[1] == '+' or tab[1] == '-'):
            index = 2

        replace_var(tab, index)
        replace_var(tab, index + 2)
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


def replace_var(tab, index):
    i = 0
    if tab[index][i] == '-':
        i += 1
    if tab[index][i] < '0' or tab[index][i] > '9':
        tab[index] = v[tab[index][i:]]
        if i == 1:
            tab[index] = "-" + tab[index]

parser = Parser()
parser.parse_file(sys.argv[1])
