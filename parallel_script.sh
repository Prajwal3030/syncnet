#!/bin/bash

# Function to process a single file
process_file() {
    eachfile="$1"
    python run_pipeline.py --videofile "$1/$eachfile" --reference wav2lip --data_dir tmp_dir
    echo "Processing $eachfile..."

    result=$(python calculate_scores_real_videos.py --videofile "$1/$eachfile" --reference wav2lip --data_dir tmp_dir)

    if [ -z "$result" ]; then
        result="99999 99999"
    fi

    echo -n "$eachfile," >> vfhq_syncnet_scores.csv
    echo "$result" | awk '{ printf "%s,%s,%s\n", $1, $2, $3 }' >> vfhq_syncnet_scores.csv

    echo "Finished processing $eachfile"
}

# Call the function with the provided argument
process_file "$1"
