# sample:12

def dummyA():
    while True:
        # Must not mutate this!
        pass

    for i in range(0, 10):
        # Must not mutate this!
        pass

def sample(*args, **kwargs):
    for a in range(0, 10): pass

    for b in [ 1, 2, 3, 4, 5 ]:
        pass

    for c in ( 1, 2, 3, 4, 5 ): s1(); s2()

    for d in range(10, 20):
        s1()
        s2()

    for e1, e2 \
        in [ ( 1, 1 ), \
             ( 2, 2 ) ]:
        s1() ; s2()

    for f in range(20, 30):
        for g in \
            [ 20, 30, 40, 50 ]:
            s1
            s2



def dummyB():
    while True:
        # Must not mutate this!
        pass

    for i in range(0, 10):
        # Must not mutate this!
        pass
