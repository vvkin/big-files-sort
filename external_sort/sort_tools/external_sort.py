import array
import numpy as np
import os
from .const import (
    BUFFER_SIZE, BUFFER_LENGTH,
    ITEM_NP, ITEM_SIZE, ITEM_TYPECODE
)
from typing import List, BinaryIO
import time


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
        start = time.time()
        self.__split()
        print(f'Split time: {time.time() - start}')
        #self.__merge()
    
    def __split(self) -> None:
        """Split target file in two files by series"""
        a_file = open(self._file_name, 'rb')
        b_file = open(self._temp_files[0], 'wb')
        c_file = open(self._temp_files[1], 'wb')

        file_number = 0 # counter to determine file to write
        last_val = float('-inf') # value to determine end of seria
        b_buffer, c_buffer = array.array(ITEM_TYPECODE), array.array(ITEM_TYPECODE)
        
        while(a_file.tell() != self._file_size): # while not eof a_file
            to_read = min(BUFFER_LENGTH, (self._file_size - a_file.tell()) // ITEM_SIZE) # buffer length or remained size
            data = array.array(ITEM_TYPECODE)
            data.fromfile(a_file, to_read)
            
            for value in data:
                file_number += (value < last_val)
                last_val = value

                if file_number & 1:
                    c_buffer.append(value)
                    if len(c_buffer) >= BUFFER_LENGTH:
                        c_buffer.tofile(c_file)
                        c_buffer = array.array(c_buffer.typecode)
                else:
                    b_buffer.append(value)
                    if len(b_buffer) >= BUFFER_LENGTH:
                        b_buffer.tofile(b_file)
                        b_buffer = array.array(b_buffer.typecode)
        
        b_buffer.tofile(b_file)
        c_buffer.tofile(c_file)

        self.__close_files(a_file, b_file, c_file)

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
