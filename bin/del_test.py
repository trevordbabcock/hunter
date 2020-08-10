#!/bin/env python

import sys


class MyTestClass():
    def __init__(self):
        self.test = 1

a = []
b = []

t = MyTestClass()
a.append(t)
a.append(t)
a.append(t)
a.append(t)
print(sys.getrefcount(t))
del a[0]
print(sys.getrefcount(t))