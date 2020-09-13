import math
import numpy as np
import os
from .const import (
   ITEM_NP, ITEM_SIZE
)

def internal_sort(file_name: str, sorted_name: str, inside_memory: int) -> None:
    """
    Sort pieces of got size in file_name file.
    Write sorted result to sorted_name file.
    """
    to_read = open(file_name, 'rb')
    to_write = open(sorted_name, 'wb')
    file_size = os.path.getsize(file_name)
    iterations = math.ceil(file_size / inside_memory)
    remained_size = file_size % inside_memory

    for counter in range(iterations):
        if counter == iterations - 1 and remained_size != 0:
            read_size = remained_size
        else:
            read_size = inside_memory
        data = np.fromfile(to_read, ITEM_NP, read_size // ITEM_SIZE)
        data = np.sort(data)
        data.tofile(to_write)
    to_read.close(); to_write.close()
