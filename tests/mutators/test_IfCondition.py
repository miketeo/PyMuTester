
from mutester.mutators.IfCondition import *
from .util import generate_mutest

TESTS = [ 'IfCondition_Func', 'IfCondition_Class' ]

for test_name in TESTS:
    func = generate_mutest(test_name, IfConditionMutator)
    globals()[func.__name__] = func
    del func
