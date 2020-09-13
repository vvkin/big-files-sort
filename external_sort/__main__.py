#!/usr/bin/env python
import os
import sys
import time
from sort_tools import external_sort


if __name__ == '__main__':
    if len(sys.argv) - ('-i' in sys.argv) != 2:  # ./script [-i] file_name
        sys.exit('Incorrect number of parameters')
    file_name = [arg for arg in sys.argv[1:] if arg != '-i'][0]
    if not os.path.isfile(file_name): # check file existence
        sys.exit(f"Path '{file_name}' does not exist or is inaccessible")
    start = time.time()
    external_sort(file_name, '-i' in sys.argv[1:]) # with internal if '-i'
    print(f'Total: {time.time() - start}')
