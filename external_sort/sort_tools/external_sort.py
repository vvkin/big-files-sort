import array
import math
import numpy as np
import os
from .const import (
    BUFFER_SIZE, BUFFER_LENGTH,
    ITEM_NP, ITEM_SIZE, ITEM_TYPECODE, 
    MB
)
from .internal_sort import internal_sort
from typing import List, BinaryIO
import psutil
import time


class ExternalSort(object):
    """
    Class to sort big numeric binary files
    using natural merge external sort
    """
    def __init__(self, file_name, sorted_len):
        self._file_name = file_name
        self._sorted_len = sorted_len # if internal sorted din't used is equal to 0
        self._available_memory = sorted_len
        self._file_size = self.__get_file_size(file_name)
        self._temp_files = ['b_file', 'c_file']
        self._is_sorted = False
    
    def __call__(self):
        """
        Method to make class callable
        executes split and merge while
        file is not sorted
        """
        while not self._is_sorted:
            if self._sorted_len == 0 or self._sorted_len > self._available_memory * 2:
                print('Unbuffered')
                self.__split()
            else:
                self.__buffered_split()
                self.__buffered_merge()
            
    def __buffered_split(self) -> None:
        """
        Split target file in two files by series.
        Is much more faster if file have equal sorted pieces
        """
        a_file = open(self._file_name, 'rb')
        b_file = open(self._temp_files[0], 'wb')
        c_file = open(self._temp_files[1], 'wb')

        remained_size = self._file_size % self._sorted_len
        file_number = 0

        while(a_file.tell() != self._file_size):
            to_read = min(self._file_size - a_file.tell(), self._sorted_len)
            data = np.fromfile(a_file, ITEM_NP, to_read // ITEM_SIZE)
            if (file_number := file_number + 1) & 1:
                data.tofile(b_file)
            else:
                data.tofile(c_file)
        
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

    def __buffered_merge(self) -> None:
        """
        Merge series from temp files and write
        it to target file. It's optimization for
        merge if internal sort was used and series
        length is not too large.
        """
        a_file = open(self._file_name, 'wb')
        b_file = open(self._temp_files[0], 'rb')
        c_file = open(self._temp_files[1], 'rb')

        b_size = self.__get_file_size(b_file.name)
        c_size = self.__get_file_size(c_file.name)
        
        iterations = 0
        
        while(b_file.tell() != b_size or c_file.tell() != c_size):
            b_read = min(b_size - b_file.tell(), self._sorted_len)
            c_read = min(c_size - c_file.tell(), self._sorted_len)
            
            to_write = np.fromfile(b_file, ITEM_NP, b_read // ITEM_SIZE)
            to_write = np.append(np.fromfile(c_file, ITEM_NP, c_read // ITEM_SIZE), to_write)
            to_write = np.sort(to_write)
            to_write.tofile(a_file)
            iterations += 1

        self._sorted_len *= 2 # after concat two series get 1 seria
        self._is_sorted = (iterations == 1) # have only two series
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
    available_memory = int(psutil.virtual_memory().available * 0.1) # 10% of available RAM
    sorted_len = available_memory * with_internal # size of sorted pieces in file
    sorted_len -= sorted_len % 8 # int number of bytes
    if with_internal: # delete old file
        print(f'Chunk size for internal sort: {sorted_len // MB} MB')
        start = time.time()
        internal_sort(file_name, sorted_name, sorted_len)
        print(f'Internal sort: {time.time() - start}s')
        os.remove(file_name)
    else: # rename file
        os.rename(file_name, sorted_name)
    ext_sort = ExternalSort(sorted_name, sorted_len)
    ext_sort() # start sorting
