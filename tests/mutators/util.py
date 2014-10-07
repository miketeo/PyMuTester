
import os, difflib, itertools, ast
from StringIO import StringIO
from mutester import codegen

def generate_mutest(test_name, mutator_klass):
    def _f():
        source_filename = os.path.join(os.path.dirname(__file__), 'depfiles', test_name + '.py')
        with open(source_filename, 'r') as source_fh:
            source_lines = source_fh.readlines()

        test_func_name, lineno = source_lines[0][1:].strip().split(':')
        test_func_lineno = int(lineno)

        buf = StringIO(codegen.to_source(ast.parse(''.join(source_lines))))
        orig_ast_lines = buf.readlines()
        buf.close()

        diffs_filename = os.path.join(os.path.dirname(__file__), 'depfiles', test_name + '.diffs')
        diffs_list, _diff = [ ], [ ]
        with open(diffs_filename, 'r') as diff_fh:
            while True:
                line = diff_fh.readline()
                if not line:
                    break
                line = line.rstrip()
                if line[:2] == '##':
                    if _diff:
                        diffs_list.append(_diff)
                        _diff = [ ]
                elif line:
                    _diff.append(line)

        if _diff:
            diffs_list.append(_diff)
        del _diff

        asts_filename = os.path.join(os.path.dirname(__file__), 'depfiles', test_name + '.asts')
        asts_list, _ast = [ ], [ ]
        with open(asts_filename, 'r') as ast_fh:
            while True:
                line = ast_fh.readline()
                if not line:
                    break
                line = line.rstrip()
                if line[:2] == '##':
                    if _ast:
                        asts_list.append(_ast)
                        _ast = [ ]
                elif line:
                    _ast.append(line)

        if _ast:
            asts_list.append(_ast)
        del _ast

        mutator = mutator_klass()
        for asts, diff, result in itertools.izip_longest(asts_list, diffs_list, mutator.mutate(source_filename, test_func_name, test_func_lineno), fillvalue = None):
            if not result:
                print 'Failed. Missing diff results'
                print '==========================='
                print 'Expecting diff'
                print '\n'.join(diff)
                assert False

            test_id, mutated_lines, mutated_ast = result
            mutated_diff = filter(lambda s: s and s[0] in ( '+', '-' ) and s != '---' and s != '+++', map(lambda s: s.rstrip(), difflib.unified_diff(source_lines, mutated_lines)))

            if not diff:
                print test_id, 'has failed. No corresponding diff found'
                print '==========================='
                print 'Result diff'
                print '\n'.join(mutated_diff)
                assert False

            if list(difflib.unified_diff(diff, mutated_diff)):
                print
                print test_id, 'has failed to match diff'
                print '==========================='
                print 'Expecting diff'
                print '\n'.join(diff)
                print 'Result diff'
                print '\n'.join(mutated_diff)
                print
                assert False

            buf = StringIO(codegen.to_source(mutated_ast))
            mutated_lines = buf.readlines()
            buf.close()
            mutated_asts = filter(lambda s: s and s[0] in ( '+', '-' ) and s != '---' and s != '+++', map(lambda s: s.rstrip(), difflib.unified_diff(orig_ast_lines, mutated_lines)))

            if not asts:
                print test_id, 'has failed. No corresponding ast found'
                print '==========================='
                print 'Result ast'
                print '\n'.join(mutated_asts)
                assert False

            if list(difflib.unified_diff(asts, mutated_asts)):
                print
                print test_id, 'has failed to match ast'
                print '==========================='
                print 'Expecting ast'
                print '\n'.join(asts)
                print 'Result ast'
                print '\n'.join(mutated_asts)
                print
                assert False

    _f.__name__ = 'test_' + test_name
    return _f
