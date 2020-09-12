import array
import numpy as np
import os
from typing import List, BinaryIO


class ExternalSort(object):
    """
    Class to sort big numeric binary files
    using natural merge external sort 
    """
    def __init__(self, file_name):
        self._file_name = file_name
        self._file_size = self.__get_file_size(file_name)
        self._temp_files = ['b_file', 'c_file']
    
    def __call__(self):
        pass
    
    @staticmethod
    def __get_file_size(file_name: str) -> int:
        """Return file size in bytes"""
        return os.path.getsize(file_name)
    
    @staticmethod
    def __close_files(*files: List[BinaryIO]) -> None:
        """Close list of binary files"""
        for file in files:
            file.close()

def external_sort(file_name: str) -> None:
    """Wrapper of functor class ExternalSort"""
    obj = ExternalSort(file_name)
    return obj()
