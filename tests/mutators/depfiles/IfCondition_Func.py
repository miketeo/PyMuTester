# FuncTest:8

def dummyA():
    if failed():
        # Must not mutate this!
        failure += 1

def FuncTest():
    # Single-line if-stmt without body
    if f1() and 1 > 2: pass

    expr()

    # Single-line if-stmt with single stmt body
    if f1() and 1 > 2: f2()

    expr()

    # Single-line if-stmt with multi-stmt body
    if f1() and 1> 2: f2(); f3(); a = a+1

    expr()

    # If-stmt with empty body and no else
    if f1():
        pass

    expr()

    # If-stmt with body and no else
    if f1() and 1 > 2:
        f2()

    # If-stmt with body and empty else
    if f1() or 2 > 3:
        f2()
    else:
        pass

    if f1() and 3 > 4:
        pass
    else:
        f2()

    # If-stmt with body and else
    if f1() and 4 == 5:
        f2()
    else:
        f3()

    # Multi/Nested-if
    if\
    f1() and 5 <= 6:
        f2()

        if f11() and 6 > 7:
            f12()
            f13()
        else:
            f14()
        f3()

        if f15():
            if f16():
                if f17():
                    f18()
            elif 2 > 3:
                f18()
            else:
                f19()
        elif 4 > 5:
            f20()
        elif 5 > 6:
            f21()
        else:
            f23()
    elif not \
        f2():
        f2()

        if f11():
            f12()
            f13()
        else:
            f14()
        f3()
    elif \
        f3() and f4() \
        or f5():
        a = a + 2
    else:
        a = a + 4

    if 10 > 20:
        f1()
    else:
        if 20 > 30:
            pass
        else:
            pass

def dummyB():
    if failed():
        # Must not mutate this!
        failure += 1
