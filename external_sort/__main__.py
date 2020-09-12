#!/usr/bin/env python
import os
import sys
from sort_tools import (
    internal_sort, external_sort
)


def main():
    if len(sys.argv) - ('-i' in sys.argv) != 2:  # ./script [-i] file_name
        sys.exit('Incorrect number of parameters')
    file_name = [arg for arg in sys.argv[1:] if arg != '-i'][0]
    f_name, extension = os.path.splitext(file_name)
    sorted_name = f_name + '_sorted' + extension
    if '-i' in sys.argv[1:]: # use internal sort and delete unsorted file
        internal_sort(file_name)
        os.remove(file_name)
    else: # rename file
        os.rename(file_name, sorted_name)
    external_sort(sorted_name)

if __name__ == '__main__':
    main()
