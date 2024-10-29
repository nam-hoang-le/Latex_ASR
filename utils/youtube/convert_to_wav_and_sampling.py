import os
from pydub import AudioSegment

def convert_and_resample_audios(input_folder, output_folder):
    """
    Recursively converts audio files in a nested folder structure to .wav format 
    with a 16 kHz sample rate and saves them in a specified output folder, 
    preserving the directory structure.
    
    Args:
    input_folder (str): Path to the root folder containing the audio files.
    output_folder (str): Path to the root folder where converted files will be saved.
    """
    # Traverse through all files in the nested folder structure
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".mp3") or filename.endswith(".wav"):
                input_file_path = os.path.join(root, filename)
                
                # Recreate the directory structure in the output folder
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_folder, relative_path)
                os.makedirs(output_dir, exist_ok=True)
                
                # Load the audio file
                audio = AudioSegment.from_file(input_file_path)
                
                # Resample to 16 kHz and export as .wav
                output_file_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.wav")
                audio.set_frame_rate(16000).export(output_file_path, format="wav")
                
                print(f"Converted and resampled {filename} to {output_file_path}")

    print("All files have been converted and resampled.")