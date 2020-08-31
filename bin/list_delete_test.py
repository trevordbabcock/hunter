#!/bin/env python

class Test():
    def __init__(self, a):
        self.a = a

    def test(self):
        print("yo")

t1 = Test("a")
t2 = Test("b")
l = [t2, t1]

l.remove(t2)

print(l[0].a)