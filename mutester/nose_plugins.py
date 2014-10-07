
__test__ = False

import os, sys
from nose.util import absdir
from nose.plugins import Plugin
from .util import is_parent_path

__all__ = [ 'MutantTracker', 'DummyPlugin' ]

class MutantTracker(Plugin):
    name = 'MutantTracker'

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option("--mutant-path", action="append",
                          default=env.get('NOSE_MUTANT_PATH'),
                          dest="mutant_path",
                          help="Restrict mutation to source files in this folder"
                          "[NOSE_MUTANT_PATH]")
        parser.add_option("--mutant-exclude", action="append",
                          default=env.get('NOSE_MUTANT_EXCLUDE'),
                          dest="mutant_exclude",
                          help="Exclude mutation on source files found in this folder"
                          "[NOSE_MUTANT_EXCLUDE]")

    def configure(self, options, conf):
        Plugin.configure(self, options, conf)
        self.stream = None
        self.enabled = True
        self.has_failed_tests = False
        self.good_tests = [ ]
        self.function_calls = { }
        self.calls = { }
        self.app_paths = filter(bool, map(normalize_path, options.mutant_path or [ ]))
        self.exclude_paths = filter(bool, map(normalize_path, options.mutant_exclude or [ ]))

    def setOutputStream(self, stream):
        self.stream = stream

    def startTest(self, test):
        sys.settrace(self.tr)
        self.calls = { }

    def afterTest(self, test):
        sys.settrace(None)
        if test.passed is not False:
            if self.calls:
                self.good_tests.append(test.address())
                self.function_calls[test.address()] = self.calls
        elif test.passed is False:
            self.has_failed_tests = True

    def tr(self, frame, event, arg):
        if event == 'call':
            if is_parent_path(os.path.dirname(frame.f_code.co_filename), self.app_paths, self.exclude_paths):
                if ( frame.f_code.co_filename, frame.f_code.co_name, frame.f_code.co_firstlineno ) not in self.calls:
                    self.calls[( frame.f_code.co_filename, frame.f_code.co_name, frame.f_code.co_firstlineno )] = frame.f_code


class DummyPlugin(Plugin):
    """Serves no functional purposes, except to declare options that are used in other plugins"""

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option("--mutant-path", action="append",
                          default=env.get('NOSE_MUTANT_PATH'),
                          dest="mutant_path",
                          help="Restrict mutation to source files in this folder"
                          "[NOSE_MUTANT_PATH]")
        parser.add_option("--mutant-exclude", action="append",
                          default=env.get('NOSE_MUTANT_EXCLUDE'),
                          dest="mutant_exclude",
                          help="Exclude mutation on source files found in this folder"
                          "[NOSE_MUTANT_EXCLUDE]")


def normalize_path(path):
    _path = absdir(path)
    if not _path:
        return ''
    return (_path + os.path.sep) if not path.endswith(os.path.sep) else _path
