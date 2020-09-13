"""Just file with constants used in external sorting"""

# Size contstants (in bytes)
MB = 1 * (10**6) # 1MB
GB = 1 * (10**9) # 1GB

# Constants about sorting items
ITEM_TYPECODE = 'q' # signed long long
ITEM_NP = 'int64' # long long in numpy
ITEM_SIZE = 8 # long long number size (in bytes)

# Constants for buffers
BUFFER_SIZE = 100 * MB
BUFFER_LENGTH = BUFFER_SIZE // ITEM_SIZE # numbers amount in buffer
