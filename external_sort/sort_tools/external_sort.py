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
        """
        Method to make class callable
        executes split and merge while
        file is not sorted
        """
        #while not self.__is_sorted():
        #    self.__split()
        #    self.__merge()
    
    def __split(self) -> None:
        """Split target file in two files by series"""
        pass

    def __merge(self) -> None:
        """Merge temp files and place it in target file"""
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
    
    def __delete_temp_files(self) -> None:
        """Delete temp files used in sorting"""
        for file_name in self._temp_files:
            os.remove(file_name)
    
    def __is_sorted(self) -> bool:
        """Check if sorting is over"""
        return (
            self.__get_file_size(self._file_name) == self._file_size and
            self.__get_file_size(self._temp_files[0]) == 0 and
            self.__get_file_size(self._temp_files[1]) == 0
        )

def external_sort(file_name: str) -> None:
    """Wrapper for functor class ExternalSort"""
    obj = ExternalSort(file_name)
    return obj()
