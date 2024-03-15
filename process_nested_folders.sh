#!/bin/bash


main_folder="$1"

current_folder=$(basename "$main_folder")  # Get the name of the current folder
output_file="${current_folder}_LSE_scores.txt"

rm "$output_file"


# Check if the main folder exists
if [ ! -d "$main_folder" ]; then
    echo "Error: Main folder does not exist."
    exit 1
fi

# Find all .mp4 files in nested folders
mp4_files=$(find "$main_folder" -type f -name "*.mp4")

# Loop over each .mp4 file and print its length
for eachfile in $mp4_files; 
do
   echo "$eachfile" >> "$output_file" 
   python run_pipeline.py --videofile "$eachfile" --reference wav2lip --data_dir tmp_dir
   python calculate_scores_real_videos.py --videofile "$eachfile" --reference wav2lip --data_dir tmp_dir >> "$output_file"
    # Append the name of the video file to the output file
done
