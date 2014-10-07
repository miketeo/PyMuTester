
import os, ast, re
from mutester import codegen
from .base import MutantTransformer

class IfConditionMutator:

    def mutate(self, source_filename, func_name, func_lineno):
        if_target = 1
        while True:
            with open(source_filename, 'rU+') as fh:
                source_lines = fh.readlines()
                fh.seek(0, os.SEEK_SET)
                node = ast.parse(fh.read(), source_filename)
                tr = IfConditionNodeTransformer(source_lines, func_name, func_lineno, if_target)
                node = tr.visit(node)
                if tr.has_mutation:
                    yield ('IFNOT-%d' % if_target), source_lines, node
                else:
                    break

            if_target += 1


class IfConditionNodeTransformer(MutantTransformer):

    IF_PAT = re.compile('^[ \t]*(if)[ \\\]')
    IFELSE_PAT = re.compile('^[ \t]*(else[: ]|elif[ \\\])')

    def __init__(self, source_lines, func_name, func_lineno, if_target):
        MutantTransformer.__init__(self, source_lines)
        self.func_list = func_name.split('.')
        self.func_lineno = func_lineno
        self.if_target = if_target
        self.if_counter = 0
        self.is_mutating = False
        self.has_mutation = False
        self.lineno_modifier = 0
        self.ifelse_set = set()

    def visit_FunctionDef(self, node):
        has_mutated = False
        if node.lineno == self.func_lineno:
            node.body.insert(0, self.prepare_mutest_import_node())
            self.is_mutating = has_mutated = True
        node = self.generic_visit(node)
        if has_mutated:
            self.is_mutating = False
        return node

    def visit_If(self, node):
        if self.if_counter > self.if_target:
            self.is_mutating = False

        if self.is_mutating:
            self.if_counter += 1

            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.ifelse_set.add(node.orelse[0])

            if self.if_counter == self.if_target:
                new_test = ast.UnaryOp(op = ast.Not(), operand = node.test)
                new_node = ast.copy_location(ast.If(test = ast.BoolOp(op = ast.Or(),
                                                                      values = [ self.prepare_mutest_reached_node(), new_test ]),
                                                    body = node.body,
                                                    orelse = node.orelse),
                                             node)

                self.has_mutation = True
                is_elif = node in self.ifelse_set

                if node.lineno == node.body[0].lineno:
                    # For those if-statements with body on the same line
                    line = self.source_lines[node.lineno + self.lineno_modifier - 1]
                    new_line = self.indentation(line) + ('elif ' if is_elif else 'if ') + codegen.to_source(new_test) + ': '
                    child_nodes = node.body[:]
                    while child_nodes:
                        n = child_nodes.pop(0)
                        new_line = new_line + codegen.to_source(n) + ('; ' if child_nodes else '')
                    new_line = new_line + '\n'
                    self.comment_line(node.lineno + self.lineno_modifier)
                    self.source_lines.insert(node.lineno + self.lineno_modifier, new_line)
                    self.lineno_modifier += 1
                else:
                    end_lineno = node.body[0].lineno
                    for start_lineno in range(end_lineno-1, 0, -1):
                        m = (self.IFELSE_PAT if is_elif else self.IF_PAT).search(self.source_lines[start_lineno + self.lineno_modifier - 1] + ' ')
                        if m:
                            break

                    # Standard if-statements with body on separate lines, or testing conditions over multiple lines
                    indent = None
                    for i in range(start_lineno, end_lineno):
                        indent = self.comment_line(i + self.lineno_modifier, indent)
                    line = self.source_lines[node.lineno + self.lineno_modifier - 1]
                    new_line = self.indentation(line) + ('elif ' if is_elif else 'if ') + codegen.to_source(new_test) + ':\n'
                    self.source_lines.insert(end_lineno + self.lineno_modifier - 1, new_line)
                    self.lineno_modifier += 1

                self.generic_visit(new_node)
                return new_node

        self.generic_visit(node)
        return node
