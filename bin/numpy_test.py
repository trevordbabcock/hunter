#!/bin/env python

import numpy as np

arr = np.zeros((3,3), dtype=bool)
arr[2,0] = True
arr[2,1] = True # y,x
arr[0,0] = True
trues = np.argwhere(arr>0)

for y,x in trues:
    #print(f"coord:{coord}")
    print(f"y:{y} x:{x}")

print(arr)
print(trues)
