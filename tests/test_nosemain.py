
import os, sys, unittest, difflib
from cStringIO import StringIO
from mutester.nose_main import main
from mutester.util import unload_modules

class NoseMainTest(unittest.TestCase):

    def setUp(self):
        self.clean_module_names = sys.modules.keys()
        self.orig_sys_argv = sys.argv[:]
        self.orig_sys_path = sys.path[:]
        sys.path.append(os.path.join(os.path.dirname(__file__)))

        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self.output_buf = StringIO()
        sys.stderr = sys.stdout = self.output_buf

    def tearDowm(self):
        unload_modules(self.clean_module_names)
        sys.argv = self.orig_sys_argv
        sys.path = self.orig_sys_path

        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
        self.output_buf.close()

    def test_cfgparser(self):
        sys.argv[1:] = [
            '--mutant-path',
            os.path.join(os.path.dirname(__file__), 'mock_modules'),
            os.path.join(os.path.dirname(__file__), 'mock_tests', '_test_cfgparser.py') + ':SafeConfigParserTestCase',
        ]
        main()

        buf_lines = self.parse_output(StringIO(self.output_buf.getvalue()))
        with open(os.path.join(os.path.dirname(__file__), 'mock_tests', '_test_cfgparser.output'), 'r') as fh:
            output_lines = self.parse_output(fh)

        diff_lines = list(difflib.unified_diff(output_lines, buf_lines, 'Expected Output', 'Test Output'))
        if diff_lines:
            assert not diff_lines, 'Test output is different\n\n' + ''.join(diff_lines)

    def parse_output(self, buf):
        lines = buf.readlines()
        while lines:
            if lines[0].startswith('Starting mutation test'):
                break
            lines.pop(0)
        return lines
