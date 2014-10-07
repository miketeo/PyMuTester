
import os, sys, logging, difflib
import nose, codegen
from .nose_plugins import MutantTracker, DummyPlugin
from .mutators import *
from .public import *
from .util import unload_modules, generate_function_names
from .importer import MutantModuleImporter

__all__ = [ 'main' ]

MUTATORS = [ IfConditionMutator(), SkipLoopMutator() ]

def main():
    clean_module_names = sys.modules.keys()
    mutant_tracker = MutantTracker()
    prog = nose.core.TestProgram(addplugins = [ mutant_tracker ], exit = False)

    ostream = mutant_tracker.stream
    if mutant_tracker.has_failed_tests:
        ostream.write('\nAt least one test has failed. All test cases must pass before we can proceed with mutation testing.\n')
        return None

    if not mutant_tracker.good_tests:
        ostream.write('\nNo working test cases with captured traces found.\n')
        ostream.write('(Please check your --mutant-path)\n')
        ostream.write('Mutation testing aborted.\n')
        return None

    ostream.write('\n')
    ostream.write('*************************\n')
    ostream.write('Starting mutation test...\n')
    ostream.write('*************************\n')

    modules_map = { }
    for module_name, module in sys.modules.iteritems():
        if hasattr(module, '__file__') and module.__file__:
            f = module.__file__
            if f.endswith('.pyc'):
                f = f[:-1]
            modules_map[f] = module_name

    source_filenames = set()
    functions_tests_map = { }  # ( filename, function_name ) -> set(test_name)
    for test_addr, function_calls in mutant_tracker.function_calls.iteritems():
        for f_addr in function_calls.iterkeys():
            source_filenames.add(f_addr[0])
            functions_tests_map.setdefault(f_addr, set()).add(make_name(test_addr))

    source_function_names = { }
    for source_filename in source_filenames:
        source_function_names[source_filename] = generate_function_names(source_filename)

    mutant_importer = MutantModuleImporter()
    mutant_importer.install()

    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = NullStdout()

    dummy_plugin = DummyPlugin()
    has_live_mutants = False
    alive_mutants, killed_mutants, unreached_mutants = 0, 0, 0
    for ( source_filename, function_name, function_lineno ), tests_set in functions_tests_map.iteritems():
        function_names = source_function_names[source_filename]
        with open(source_filename, 'rU') as fh:
            source_lines = fh.readlines()

        ostream.write('Mutating %s (%s:%d)...\n' % ( function_names.get(function_lineno, function_name), source_filename, function_lineno ))
        for mutator in MUTATORS:
            for mutant_id, modified_lines, modified_ast in mutator.mutate(source_filename, function_name, function_lineno):
                ostream.write('*** %s... ' % mutant_id)

                unload_modules(clean_module_names)
                mutest_reset()

                modified_source = codegen.to_source(modified_ast)
                mutant_importer.override(modules_map[source_filename], compile(modified_source, source_filename, 'exec'))

                suite = prog.testLoader.loadTestsFromNames(tests_set)
                success = nose.run(addplugins = [ mutant_tracker ], suite = suite)

                if mutest_has_reached():
                    if success:
                        alive_mutants += 1
                        has_live_mutants = True
                        ostream.write('Mutant alive !!!\n')
                        ostream.write('\n'.join(filter(lambda s: not s[1:].lstrip().startswith('#Mutant# '), map(lambda s: s.rstrip(), difflib.unified_diff(source_lines, modified_lines, source_filename + ' (original)', source_filename + ' (mutant-' + mutant_id + ')')))))
                        ostream.write('\n')
                    else:
                        killed_mutants += 1
                        ostream.write('Mutant killed\n')
                else:
                    unreached_mutants += 1
                    ostream.write('Mutant not reached\n')
                    ostream.write('\n'.join(filter(lambda s: not s[1:].lstrip().startswith('#Mutant# '), map(lambda s: s.rstrip(), difflib.unified_diff(source_lines, modified_lines, source_filename + ' (original)', source_filename + ' (mutant-' + mutant_id + ')')))))
                    ostream.write('\n')

    sys.stdout, sys.stderr = orig_stdout, orig_stderr
    total_mutants = alive_mutants + killed_mutants + unreached_mutants
    if total_mutants > 0:
        ostream.write('\nMutant Test Results\n')
        ostream.write('Total: %d\n' % total_mutants)
        ostream.write('\tAlive: %d (%0.1f%%)\tKilled: %d (%0.1f%%)\tUnreachable: %d (%0.1f%%)\n' % ( alive_mutants, alive_mutants*100.0/total_mutants, killed_mutants, killed_mutants*100.0/total_mutants, unreached_mutants, unreached_mutants*100.0/total_mutants ))

    return has_live_mutants, alive_mutants, killed_mutants, unreached_mutants


def make_name(test_addr):
    filename, module, call = test_addr
    if filename is not None:
        head = nose.util.src(filename)
    else:
        head = module
    if call is not None:
        return "%s:%s" % (head, call)
    return head


class NullStdout():

    def write(self, str):
        pass

    def writelines(self, str):
        pass


if __name__ == '__main__':
    main()
