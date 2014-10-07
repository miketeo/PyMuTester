
from mutester.mutators.SkipLoop import *
from .util import generate_mutest

TESTS = [ 'SkipLoop_For', 'SkipLoop_While' ]

for test_name in TESTS:
    func = generate_mutest(test_name, SkipLoopMutator)
    globals()[func.__name__] = func
    del func
