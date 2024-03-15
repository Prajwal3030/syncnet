rm avijit_scores.txt

yourfolder=$1

find "$yourfolder" -type f -name "*.mp4" -o -name "*.avi" -o -name "*.mkv" | while read -r eachfile
do
   echo "$eachfile" >> avijit_scores.txt 
   python run_pipeline.py --videofile "$eachfile" --reference wav2lip --data_dir tmp_dir
   python calculate_scores_real_videos.py --videofile "$eachfile" --reference wav2lip --data_dir tmp_dir >> avijit_scores.txt
done
