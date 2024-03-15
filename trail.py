import os
import subprocess
import csv
import random

def download_vid(file_number, destination_path):
    download_command = "gcloud storage cp gs://unai-videodata/celebv_text/video/celebvtext_{:06}.mp4 {}".format(file_number, destination_path)
    try:
        subprocess.run(download_command, shell=True)
        print('Downloaded celebvtext_{:06}.mp4 successfully.'.format(file_number))
    except subprocess.CalledProcessError as e:
        print('Error downloading file: {}'.format(e))

def download_audio(file_number, destination_path):
    download_command = "gcloud storage cp gs://unai-videodata/celebv_text/clean_audio/celebvtext_{:06}.wav {}".format(file_number, destination_path)
    try:
        subprocess.run(download_command, shell=True)
        print('Downloaded celebvtext_{:06}.wav successfully.'.format(file_number))
    except subprocess.CalledProcessError as e:
        print('Error downloading file: {}'.format(e))

def merge_video_audio(video_path, audio_path, output_path):
    merge_command = "ffmpeg -i {} -i {} -c:v copy -c:a aac -strict experimental {}".format(video_path, audio_path, output_path)
    try:
        subprocess.run(merge_command, shell=True)
        print('Merged video and audio successfully.')
    except subprocess.CalledProcessError as e:
        print('Error merging files: {}'.format(e))

def delete_files(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)

def calculate_score(combined_folder):
    calculate_command = "./calculate_scores.sh {}".format(combined_folder)
    try:
        subprocess.run(calculate_command, shell=True)
        print("Score calculated and saved in the CSV file.")
    except subprocess.CalledProcessError as e:
        print("Error calculating score: {}".format(e))

def read_csv_and_save_to_txt(csv_file_path, txt_file_path):
    # Read data from CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        data = [row for row in csv_reader]

    # Save data to TXT file
    with open(txt_file_path, 'a') as txt_file:
        for row in data[1:]:  # Skip the first row (headers)
            # Customize the format based on your requirements
            line = '\t'.join(row) + '\n'
            txt_file.write(line)


def main():
    max_iterations = 3000
    
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(CURR_DIR, 'syncnet_scores.csv')
    scores = os.path.join(CURR_DIR, 'scores.txt')
    iteration=2001

    for iteration in range(iteration,max_iterations+1):
        audio_folder_path = os.path.join(CURR_DIR, 'audio')
        video_folder_path = os.path.join(CURR_DIR, 'video')
        combined_folder_path = os.path.join(CURR_DIR, 'comb')

        download_vid(iteration, video_folder_path)
        download_audio(iteration, audio_folder_path)

        video_file = os.path.join(video_folder_path, 'celebvtext_{:06}.mp4'.format(iteration))
        audio_file = os.path.join(audio_folder_path, 'celebvtext_{:06}.wav'.format(iteration))
        output_file = os.path.join(combined_folder_path, 'celebvtext_{:06}.mp4'.format(iteration))

        #Check if both video and audio files exist before merging
        if os.path.exists(video_file) and os.path.exists(audio_file):
            merge_video_audio(video_file, audio_file, output_file)
            calculate_score(combined_folder_path)
            read_csv_and_save_to_txt(csv_path, scores)
            delete_files(combined_folder_path)
        else:
            print('Skipping merge for iteration {}: Video or audio file not found.'.format(iteration))

        delete_files(video_folder_path)
        delete_files(audio_folder_path)
      
if __name__ == "__main__":
    main()