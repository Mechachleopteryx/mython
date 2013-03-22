#! /usr/bin/env python
# ______________________________________________________________________
# Module imports

import ast

from mython.lang.python.astify import MyHandler

# ______________________________________________________________________
# Class definitions

class MyStmt(ast.stmt):
    '''In ASDL:
    stmt = ...
         | MyStmt(expr? lang,
                  identifier? name,
                  arguments? args,
                  string body,
                  int body_ofs)
         | ...
    '''
    _fields = ('lang', 'name', 'args', 'body', 'body_ofs')

# ______________________________________________________________________

class MyExpr(ast.expr):
    '''In ASDL:
    expr = ...
         | MyExpr(expr? elang, string estr)
         | ...
    '''
    _fields = ('elang', 'estr')

# ______________________________________________________________________

class MyConcreteTransformer(MyHandler):
    def handle_not_test(self, node):
        children = node[1]
        child_count = len(children)
        assert child_count > 0
        first_child = children[0][0]
        if isinstance(first_child, tuple) and (first_child[1] == '!'):
            location = first_child[2]
            elang = None
            if child_count == 2:
                estr = self.handle_node(children[1][0][1])
            else:
                assert child_count == 5
                elang = self.handle_node(children[2])
                estr = self.handle_node(children[4])
            ret_val = MyExpr(elang, estr,
                             lineno=location[0], col_offset=location[1])
        else:
            ret_val = super(MyConcreteTransformer, self).handle_not_test(node)
        return ret_val

    def handle_compound_stmt(self, node):
        ret_val = super(MyConcreteTransformer, self).handle_compound_stmt(node)
        return ret_val

    def handle_mysuite(self, node):
        raise NotImplementedError()

    def handle_myexpr(self, node):
        _, children = node
        assert len(children) == 2
        return children[-1][0][1][:-1]

    handle_myexpr1 = handle_myexpr

# ______________________________________________________________________

class MyAbstractTransformer(ast.NodeTransformer):
    def visit_MyStmt(self, node):
        raise NotImplementedError()

    def visit_MyExpr(self, node):
        raise NotImplementedError()

# ______________________________________________________________________
# Main (self-test) routine

def main(*args, **kws):
    import ast
    for myast_cls in (MyStmt, MyExpr):
        assert issubclass(myast_cls, ast.AST), myast_cls
        fields = range(len(myast_cls._fields))
        node = myast_cls(*fields)
        results = list(expected == actual
                       for expected, actual in zip(zip(myast_cls._fields,
                                                       fields),
                                                   ast.iter_fields(node)))
        assert all(results), (node, results)

# ______________________________________________________________________

if __name__ == "__main__":
    main()

# ______________________________________________________________________
# End of mython.myast