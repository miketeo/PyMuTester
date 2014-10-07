
import os, sys, ast
from nose.util import absdir

__all__ = [ 'is_parent_path', 'unload_modules', 'generate_function_names' ]


def is_parent_path(path, parents, excludes = [ ]):
    """Returns True if path is a child folder of one of the paths in parents, but not excluded under excludes"""
    _path = absdir(os.path.expanduser(os.path.expandvars(path)))
    if not _path:
        return False

    if not _path.endswith(os.path.sep):
        _path = _path + os.path.sep

    for p in parents:
        if os.path.commonprefix([ _path, p ]) == p:
            for excl in excludes:
                if os.path.commonprefix([ _path, excl ]) == excl:
                    return False
            return True

    return False

def unload_modules(clean_modules):
    """Unload all modules in sys.modules that are not found in clean_modules"""
    for k in sys.modules.keys():
        if k not in clean_modules:
            del sys.modules[k]

class FunctionNameVisitor(ast.NodeVisitor):

    def __init__(self):
        self.function_stack = [ ]
        self.function_names = { }

    def visit_ClassDef(self, node):
        self.function_stack.append(node.name)
        self.function_names[node.lineno] = '.'.join(self.function_stack)
        n = self.generic_visit(node)
        self.function_stack.pop()
        return n

    def visit_FunctionDef(self, node):
        self.function_stack.append(node.name)
        self.function_names[node.lineno] = '.'.join(self.function_stack)
        n = self.generic_visit(node)
        self.function_stack.pop()
        return n


def generate_function_names(source_filename):
    with open(source_filename, 'rU') as fh:
        node = ast.parse(fh.read(), source_filename)

        visitor = FunctionNameVisitor()
        visitor.visit(node)
        return visitor.function_names
