#!/bin/bash

parent_directory="$1"

# Check if the parent directory exists
if [ ! -d "$parent_directory" ]; then
    echo "Error: Parent directory does not exist."
    exit 1
fi

# Loop over each subfolder in the parent directory
for subfolder in "$parent_directory"/*/; do
    subfolder_name=$(basename "$subfolder")
    echo "Processing subfolder: $subfolder_name"
    
    # Run the script on the subfolder
    (source process_nested_folders.sh "$subfolder")
    
    echo "--------------------"
done
