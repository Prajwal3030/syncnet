#!/bin/bash

# Check if the input parent directory is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 /path/to/parent/directory"
    exit 1
fi

# Input parent directory
input_parent_directory="$1"

# Iterate through each folder in the input parent directory
for folder in "$input_parent_directory"/*; do
    # Check if the path is a directory
    if [ -d "$folder" ]; then
        echo "Processing videos in: $folder"
        # Run the provided code on the current folder
        rm -f "$folder/all_scores.txt"
        yourfilenames=$(ls "$folder")
        for eachfile in $yourfilenames; do
            python run_pipeline.py --videofile "$folder/$eachfile" --reference wav2lip --data_dir tmp_dir
            python calculate_scores_real_videos.py --videofile "$folder/$eachfile" --reference wav2lip --data_dir tmp_dir >> "$folder/all_scores.txt"
        done
        echo "Finished processing videos in: $folder"
    fi
done

echo "Processing completed for all folders in the parent directory."
