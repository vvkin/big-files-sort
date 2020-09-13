import array
import math
import numpy as np
import struct
import os
from .const import (
    ITEM_NP, ITEM_SIZE, ITEM_TYPECODE, MB
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
    def __init__(self, file_name, sorted_len, buffer_size):
        self._file_name = file_name
        self._sorted_len = sorted_len # if internal sorted din't used is equal to 0
        self._available_memory = sorted_len
        self._buffer_size = buffer_size
        self._buffer_len = buffer_size // ITEM_SIZE
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
                self.__split()
                self.__merge()
            else:
                self.__buffered_split()
                self.__buffered_merge()
        self.__delete_temp_files()
            
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
            to_read = min(self._buffer_size, self._file_size - a_file.tell()) # buffer length or remained size
            data = array.array(ITEM_TYPECODE)
            data.fromfile(a_file, to_read // ITEM_SIZE)
            
            for value in data:
                file_number += (value < last_val)
                last_val = value

                if file_number & 1:
                    c_buffer.append(value)
                    if len(c_buffer) >= self._buffer_len:
                        c_buffer.tofile(c_file)
                        c_buffer = array.array(c_buffer.typecode)
                else:
                    b_buffer.append(value)
                    if len(b_buffer) >= self._buffer_len:
                        b_buffer.tofile(b_file)
                        b_buffer = array.array(b_buffer.typecode)
        
        b_buffer.tofile(b_file)
        c_buffer.tofile(c_file)
        self._is_sorted = (file_number < 2) # here are only two series
        
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
        """
        Merge series in temporary files and
        write it to target file"""

        sfile = open(self._file_name, "wb")  
        files = [open(fname, "rb") for fname in self._temp_files]
        
        fsizes = [*map(self.__get_file_size, self._temp_files)]
        masked = [False, False]
       
        def buffer_generator(files):
            for idx, file in enumerate(files):
                chunk = min(fsizes[idx] // ITEM_SIZE, self._buffer_len)
                yield np.fromfile(file, ITEM_NP,  chunk)
        
        merged_buffer = np.zeros(self._buffer_len, dtype=ITEM_NP)
        buffers = [buffer for buffer in buffer_generator(files)]
        idxs, merge_idx = [0, 0], 0

        while True:
            
            if masked[0] or masked[1]:
                midx = 1 if masked[0] else 0
            
            else: midx = 0 if buffers[0][idxs[0]]\
                < buffers[1][idxs[1]] else 1
            
            merged_buffer[merge_idx] = buffers[
                    midx][idxs[midx]]
            
            idxs[midx] += 1; merge_idx += 1
            
            if merge_idx == self._buffer_len:
                
                merged_buffer.tofile(sfile); merge_idx = 0
                merged_buffer = np.zeros(self._buffer_len, dtype=ITEM_NP)
            
            if idxs[midx] == buffers[midx].shape[0]:
                
                chunk = min(self._buffer_len, fsizes[midx] -\
                        files[midx].tell())
                
                last = buffers[midx][-1]
                
                if not chunk:
                    
                    merged_buffer[:merge_idx].tofile(sfile)
                    
                    oidx = (midx + 1) % 2
                    
                    buffers[oidx][
                            idxs[oidx]:].tofile(sfile)
                    
                    sfile.write(files[oidx].read())
                    
                    break
                
                buffers[midx] = np.fromfile(
                    files[midx], ITEM_NP, chunk)
                
                if buffers[midx][0] < last:
                    masked[midx] = True
                
                idxs[midx] = 0
                
            if idxs[midx] and buffers[midx][idxs[midx]]\
                < buffers[midx][idxs[midx] - 1]:
                masked[midx] = True
                
            if masked[0] and masked[1]:
                masked = [False, False] 
        
        self.__close_files(sfile, files[0], files[1])

    @staticmethod
    def __get_file_size(file_name: str) -> int:
        """Return file size in bytes"""
        return os.path.getsize(file_name)
    
    @staticmethod
    def __overwrite_files(f_file: BinaryIO, s_file: BinaryIO) -> None:
        """Write all data from f_file to s_file with little RAM using"""
        f_size = os.path.getsize(f_file.name)
        for _ in range(0, f_size, BUFFER_SIZE):
            to_read = min(f_size - f_file.tell(), BUFFER_SIZE)
            to_write = np.fromfile(f_file, ITEM_NP, to_read // ITEM_SIZE)
            to_write.tofile(s_file)

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
    available_memory = psutil.virtual_memory().available # available RAM
    sorted_len = int(available_memory * 0.08 * with_internal) # size of sorted pieces in file (8% of available)
    sorted_len -= sorted_len % 8 # int number of bytes
    buffer_size = int(available_memory * 0.1) # 10% of available RAM
    buffer_size -= buffer_size % 8 # int number of bytes
    print(f'Buffer size: {buffer_size // MB} MB')
    if with_internal: # delete old file
        print(f'Chunk size for internal sort: {sorted_len // MB} MB')
        start = time.time()
        internal_sort(file_name, sorted_name, sorted_len)
        print(f'Internal sort: {time.time() - start}s')
        os.remove(file_name)
    else: # rename file
        os.rename(file_name, sorted_name)
    ext_sort = ExternalSort(sorted_name, sorted_len, buffer_size)
    start = time.time()
    ext_sort() # start sorting
    print(f'External_sort: {time.time() - start}s')
