import array
import numpy as np
import os
from .const import (
    BUFFER_SIZE, BUFFER_LENGTH,
    ITEM_NP, ITEM_SIZE, ITEM_TYPECODE, 
    INSIDE_MEMORY
)
from .internal_sort import internal_sort
from typing import List, BinaryIO
import time


class ExternalSort(object):
    """
    Class to sort big numeric binary files
    using natural merge external sort
    """
    def __init__(self, file_name, sorted_len):
        self._file_name = file_name
        self._sorted_len = sorted_len # if internal sorted din't used is equal to 0
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
        if self._sorted_len == 0:
            self.__split()
        else:
            self.__buffered_split()
        print(f'Split time: {time.time() - start}')
        #self.__merge()
    
    def __buffered_split(self) -> None:
        """
        Split target file in two files by series.
        Is much more faster if file have equal sorted pieces
        """
        a_file = open(self._file_name, 'rb')
        b_file = open(self._temp_files[0], 'wb')
        c_file = open(self._temp_files[1], 'wb')

        remained_size = self._file_size % self._sorted_len
        iterations_num = self._file_size // self._sorted_len

        for counter in range(iterations_num):
            if counter == iterations_num - 1 and remained_size != 0:
                to_read = remained_size
            else:
                to_read = self._sorted_len
            data = np.fromfile(a_file, ITEM_NP, to_read // ITEM_SIZE)
            if counter & 1:
                data.tofile(c_file)
            else:
                data.tofile(b_file)

        self._sorted_len *= 2 # after merge two equal sequences get one double sequence
        self.__close_files(a_file, b_file, c_file)


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

def external_sort(file_name: str, with_internal: bool) -> None:
    """
    Wrapper for ExternalSort functor.
    Sort big numeric binary files using 
    natural merge external sort. Can be used
    with internal sort to make sorted pieces in file
    before sorting
    """
    f_name, extension = os.path.splitext(file_name)
    sorted_name = f_name + '_sorted' + extension
    sorted_len = INSIDE_MEMORY * with_internal
    if with_internal: # delete old file
        INSIDE_MEMORY = os.path.getsize(a_file) // 4
        internal_sort(file_name, sorted_name)
        os.remove(file_name)
    else: # rename file
        os.rename(file_name, sorted_name)
    ext_sort = ExternalSort(sorted_name, sorted_len)
    ext_sort() # start sorting
