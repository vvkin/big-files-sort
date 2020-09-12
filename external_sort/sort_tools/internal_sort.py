import math
import numpy as np
import os
from .const import (
    INSIDE_MEMORY, NUMBERS_PER_READ, ITEM_NP, ITEM_SIZE
)

def internal_sort(file_name: str, sorted_name: str) -> None:
    """
    Sort pieces in file in file_name file.
    Write sorted result to sorted_name file.
    """
    to_read = open(file_name, 'rb')
    to_write = open(sorted_name, 'wb')
    file_size = os.path.getsize(file_name)
    iterations = math.ceil(file_size / INSIDE_MEMORY)
    remained_size = file_size % INSIDE_MEMORY

    for counter in range(iterations):
        if counter == iterations - 1 and remained_size != 0:
            read_size = remained_size // ITEM_SIZE
        else:
            read_size = NUMBERS_PER_READ
        data = np.fromfile(to_read, ITEM_NP, read_size)
        data = np.sort(data)
        data.tofile(to_write)
    
    to_read.close(); to_write.close()
