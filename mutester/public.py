
import types

__all__ = [ 'mutest_reset', 'mutest_statement_reached', 'mutest_has_reached', 'mutest_is_filetype' ]

_mutest_ok = False
_mutest_counter = 0

def mutest_reset():
    global _mutest_ok, _mutest_counter
    _mutest_ok = False
    _mutest_counter = 0

def mutest_statement_reached():
    global _mutest_ok, _mutest_counter
    _mutest_ok = True
    _mutest_counter += 1
    return _mutest_counter

def mutest_has_reached():
    global _mutest_ok
    return _mutest_ok

def mutest_is_filetype(obj):
    return type(obj) is types.FileType
