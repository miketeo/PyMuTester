
import sys, imp


class MutantModuleImporter:

    def __init__(self):
        self.override_name = None
        self.override_code = None

    def install(self):
        sys.meta_path.insert(0, self)

    def override(self, module_name, module_code):
        self.override_name = module_name
        self.override_code = module_code

    def find_module(self, fullname, path = None):
        if fullname == self.override_name:
            return self
        return None

    def load_module(self, fullname):
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = '<%s>' % self.__class__.__name__
        mod.__loader__ = self
        mod.__path__ = [ ]
        exec self.override_code in mod.__dict__
        return mod
