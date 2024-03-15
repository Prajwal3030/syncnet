#!/bin/bash

# Check if directory argument is provided
if [ -z "$1" ]; then
    echo "No directory provided."
    exit 1
fi

# Directory containing video files
VIDEO_DIR="$1"

# Create or overwrite the CSV file with headers
echo "Filename,Distance,Confidence" > syncnet_scores.csv

# Loop through each video file in the directory
for videofile in "$VIDEO_DIR"/*.mp4; do
    echo "Processing file: $videofile"

    # Check if file is a valid video file and has audio
    if ! ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$videofile" > /dev/null || \
       ! ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$videofile" > /dev/null; then
        echo "Invalid file or audio missing: $videofile"
        echo "$videofile,NA,NA" >> syncnet_scores.csv
        continue
    fi

    # Run the pipeline script
    if ! python run_pipeline.py --videofile "$videofile" --data_dir tmp_dir; then
        echo "Error processing file: $videofile"
        echo "$videofile,NA,NA" >> syncnet_scores.csv
        continue
    fi

    # Run the calculate scores script and capture its output
    output=$(python calculate_scores_real_videos.py --videofile "$videofile" --data_dir tmp_dir)
    
    # Check if the output contains two numbers for distance and confidence
    if [[ $output =~ ([0-9.]+)[[:space:]]+([0-9.]+) ]]; then
        distance=${BASH_REMATCH[1]}
        confidence=${BASH_REMATCH[2]}
    else
        distance="NA"
        confidence="NA"
    fi

    # Append results to the CSV file
    echo "$videofile,$distance,$confidence" >> syncnet_scores.csv
done

echo "Processing complete. Scores saved in syncnet_scores.csv"
