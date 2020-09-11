#!/bin/bash

# Usage
# chmod +x generate_file.sh
# ./generate_file.sh [file_name] [file_size] (MB, GB, KB etc.)

FILE_NAME="$PWD/$1" # absolulte path to file
FILE_SIZE=${2^^[a-z]} # file size to upper

head -c $FILE_SIZE < /dev/urandom > "${FILE_NAME}"