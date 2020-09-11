"""Script to sort large numeric files"""
import sys
import os
from sort_tools.internal_sort import internal_sort


def main():
    if len(sys.argv) - ('-i' in sys.argv) != 2:  # ./script [-i] file_name
        sys.exit('Incorrect number of parameters')
    file_name = [arg for arg in sys.argv[1:] if arg != '-i'][0]
    if '-i' in sys.argv[1:]: # use internal sort
        internal_sort(file_name)
    else:
        f_name, extension = os.path.splitext(file_name)
        file_name = f_name + '_sorted' + extension
    # TODO: execute external sort

if __name__ == '__main__':
    main()
