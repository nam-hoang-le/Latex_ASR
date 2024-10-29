from pydub.utils import mediainfo
import os

# Function to get the duration of an audio file
def get_audio_duration(file_path):
    try:
        info = mediainfo(file_path)
        duration_in_sec = float(info['duration'])
        return duration_in_sec
    except Exception as e:
        print(f"Could not read duration for file: {file_path}, error: {e}")
        return 0.0

# Recursive function to process all directories and audio files
def process_audio_files_in_nested_folders(folder_path):
    total_duration = 0.0  # Variable to hold the total duration (in seconds)

    # Traverse all directories and files in the root folder
    for root, dirs, files in os.walk(folder_path):
        folder_total_duration = 0.0
        # Process each file in the current folder
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                duration = get_audio_duration(file_path)
                folder_total_duration += duration
                print(f"File: {file}, Duration: {duration:.2f} seconds")

        # Print the total duration for the current folder
        if folder_total_duration > 0:
            print(f"Total duration in folder '{root}': {folder_total_duration / 3600:.2f} hours")

        total_duration += folder_total_duration

    # Convert total duration from seconds to hours
    total_duration_in_hours = total_duration / 3600
    print(f"Total duration of all files: {total_duration_in_hours:.2f} hours")
    return total_duration_in_hours