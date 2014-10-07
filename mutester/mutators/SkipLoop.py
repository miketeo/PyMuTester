
import os, ast
from mutester import codegen
from .base import MutantTransformer

class SkipLoopMutator:

    def mutate(self, source_filename, func_name, func_lineno):
        loop_target = 1
        while True:
            with open(source_filename, 'rU+') as fh:
                source_lines = fh.readlines()
                fh.seek(0, os.SEEK_SET)
                node = ast.parse(fh.read(), source_filename)
                tr = SkipLoopNodeTransformer(source_lines, func_name, func_lineno, loop_target)
                node = tr.visit(node)
                if tr.has_mutation:
                    yield ('SKIPLOOP-%d' % loop_target), source_lines, node
                else:
                    break

            loop_target += 1


class SkipLoopNodeTransformer(MutantTransformer):

    def __init__(self, source_lines, func_name, func_lineno, loop_target):
        MutantTransformer.__init__(self, source_lines)
        self.func_list = func_name.split('.')
        self.func_lineno = func_lineno
        self.loop_target = loop_target
        self.loop_counter = 0
        self.is_mutating = False
        self.has_mutation = False
        self.lineno_modifier = 0

    def visit_FunctionDef(self, node):
        has_mutated = False
        if node.lineno == self.func_lineno:
            node.body.insert(0, self.prepare_mutest_import_node())
            self.is_mutating = has_mutated = True
        node = self.generic_visit(node)
        if has_mutated:
            self.is_mutating = False
        return node

    def visit_For(self, node):
        return self._processVisit(node, 'for')

    def visit_While(self, node):
        return self._processVisit(node, 'while')

    def _processVisit(self, node, loop_name):
        if self.loop_counter > self.loop_target:
            self.is_mutating = False

        if self.is_mutating:
            self.loop_counter += 1

            if self.loop_counter == self.loop_target:
                self.has_mutation = True
                start_lineno = node.lineno
                body_lineno = node.body[0].lineno
                line = self.source_lines[node.lineno + self.lineno_modifier - 1]

                if node.lineno == body_lineno:
                    # For those loop-statements with body on the same line
                    end_lineno = node.lineno + 1
                    body_indentation = self.indentation(line) + '    '
                    if isinstance(node.body[0], ast.Pass):
                        node.body.pop(0)
                else:
                    end_lineno = body_lineno
                    body_indentation = self.indentation(self.source_lines[body_lineno + self.lineno_modifier - 1])
                    if isinstance(node.body[0], ast.Pass):
                        n = node.body.pop(0)
                        end_lineno += 1

                node.body.insert(0, ast.parse('if mutest_statement_reached() % 2 == 0: continue'))

                new_lines = [ ]
                if loop_name == 'for':
                    new_lines.append(self.indentation(line) + 'for ' + codegen.to_source(node.target) + ' in ' + codegen.to_source(node.iter) + ':\n')
                else:
                    new_lines.append(self.indentation(line) + 'while ' + codegen.to_source(node.test) + ':\n')

                new_lines.append(body_indentation + 'if mutest_statement_reached() % 2 == 0: continue\n')
                if node.lineno == body_lineno:
                    for n in node.body[1:]: # The first line "if mutest_statement_reached() % 2 == 0: continue" is already inserted
                        new_lines.append(body_indentation + codegen.to_source(n) + '\n')

                indent = None
                for i in range(start_lineno, end_lineno):
                    indent = self.comment_line(i + self.lineno_modifier, indent)

                self.source_lines[end_lineno-1+self.lineno_modifier:end_lineno-1+self.lineno_modifier] = new_lines
                self.lineno_modifier += len(new_lines)

        self.generic_visit(node)
        return node
