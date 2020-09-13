#!/usr/bin/env python

import sys
import os
import numpy as np
from numba import njit

@njit
def is_sorted(arr):
    for i in range(arr.size-1):
        if arr[i+1] < arr[i]: return False
    return True

# to make check much more faster
if __name__ == '__main__':
    """Check is file sorted"""
    if len(sys.argv) != 2:
        sys.exit('Incorrect number of parameters')
    file_name = sys.argv[1]
    if not os.path.isfile(file_name): # check file existence
        sys.exit(f"Path '{file_name}' does not exist or is inaccessible")
    
    file = open(file_name, 'rb')
    data = np.fromfile(file, 'int64')
    print(is_sorted(data))
    file.close()

