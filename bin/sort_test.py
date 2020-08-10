#!/bin/env python

from time import time

class Event:
    def __init__(self, time):
        self.time = time

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time


a = [Event(2), Event(3), Event(1)]
print(a[0].time)
print(a[1].time)
print(a[2].time)
a = sorted(a)
print("-----------")
print(a[0].time)
print(a[1].time)
print(a[2].time)
