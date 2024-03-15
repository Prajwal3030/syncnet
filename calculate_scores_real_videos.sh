#!/bin/bash

# Check if directory argument is provided
if [ -z "$1" ]; then
    echo "No directory provided."
    exit 1
fi

# Create or overwrite the CSV file with headers
echo "Filename,Distance,Confidence" > VFHQ_syncnet_scores.csv

# Get the list of filenames in the provided directory
yourfilenames=$(ls "$1")

# Loop through each file in the directory
for eachfile in $yourfilenames; do
   python run_pipeline.py --videofile "$1/$eachfile" --reference wav2lip --data_dir tmp_dir

   # Run calculate_scores_real_videos.py and capture its output
   output=$(python calculate_scores_real_videos.py --videofile "$1/$eachfile" --reference wav2lip --data_dir tmp_dir)

   # Check if the output contains two numbers
   if [[ $output =~ ([0-9.]+)[[:space:]]+([0-9.]+) ]]; then
       distance=${BASH_REMATCH[1]}
       confidence=${BASH_REMATCH[2]}
   else
       distance="NA"
       confidence="NA"
   fi

   # Append to the CSV file
   echo "$eachfile,$distance,$confidence" >> VFHQ_syncnet_scores.csv
done
