# sample:12

def dummyA():
    while True:
        # Must not mutate this!
        pass

    for i in range(0, 10):
        # Must not mutate this!
        pass

def sample(*args, **kwargs):
    while 1 > 2 and 2 > 3: pass

    while 2 > 3 and 4 > 5:
        pass

    while 3 > 4 or 5 > 6: s1(); s2()

    while 4 > 5 or 5 > 6:
        s1()
        s2()

    while \
        5 > 6 \
        or 6 > 7:
        s1() ; s2()

    while 10 > 20 and 20 > 30:
        while a > b \
            and c != d:
            s1
            s2



def dummyB():
    while True:
        # Must not mutate this!
        pass

    for i in range(0, 10):
        # Must not mutate this!
        pass
