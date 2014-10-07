
import sys, re, ast


INDENT_PAT = re.compile('^([ \t]*)[^ \t]', re.MULTILINE)

class MutantTransformer(ast.NodeTransformer):

    def __init__(self, source_lines):
        self.source_lines = source_lines

    def comment_line(self, lineno, indent = None):
        line = self.source_lines[lineno-1]
        if indent is None:
            indent = self.indentation(line)
        self.source_lines[lineno-1] = (indent + '#Mutant#  ' + line[len(indent):]).rstrip() + '\n'
        return indent

    def indentation(self, line):
        m = INDENT_PAT.search(line)
        if m:
            return m.group(1)
        return ''

    def prepare_mutest_import_node(self):
        return ast.ImportFrom(module = 'mutester.public', names = [ ast.alias(name = 'mutest_statement_reached', asname = None) ], level = 0)

    def prepare_mutest_reached_node(self):
        return ast.Call(func = ast.Name(id = 'mutest_statement_reached'), args = [ ], keywords = [ ], starargs = None, kwargs = None)

    def print_source_lines(self):
        for lineno, line in enumerate(self.source_lines):
            sys.stdout.write('%03d: %s' % ( lineno+1, line ))
