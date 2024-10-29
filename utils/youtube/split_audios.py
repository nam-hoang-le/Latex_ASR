import librosa
import numpy as np
import os
import soundfile as sf

# Function to split audio at the point with the lowest frequency in a given time range
def split_audio_at_lowest_frequency(
    file_path, output_dir, min_length=10, max_length=15
):
    print(f"Processing file: {file_path}")

    # Load audio file
    audio, sr = librosa.load(file_path, sr=None)

    # Create directory for storing audio segments if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize variables for audio segmentation
    segment_start = 0
    segment_count = 0

    while segment_start < len(audio):
        # Define search range for the cut point
        search_end = min(segment_start + int(max_length * sr), len(audio))
        search_start = segment_start + int(min_length * sr)

        if search_start >= len(audio):
            break

        # Calculate RMS energy for the search segment
        search_segment = audio[search_start:search_end]
        rms = librosa.feature.rms(y=search_segment, frame_length=2048, hop_length=512)[
            0
        ]

        # Find frame with the lowest RMS energy
        min_energy_frame = np.argmin(rms)

        # Calculate the cut point in samples
        cut_time = min_length + librosa.frames_to_time(
            min_energy_frame, sr=sr, hop_length=512
        )
        cut_sample = segment_start + int(cut_time * sr)

        # Extract audio segment
        segment_to_save = audio[segment_start:cut_sample]

        # Save the audio segment
        output_file = os.path.join(output_dir, f"segment_{segment_count:03d}.mp3")
        sf.write(output_file, segment_to_save, sr)

        print(
            f"Created segment {segment_count:03d} from {segment_start/sr:.2f}s to {cut_sample/sr:.2f}s"
        )

        # Update start position for the next segment
        segment_start = cut_sample
        segment_count += 1


# Function to process all audio files in a nested folder structure
def process_audio_files_in_nested_folder(
    input_folder, output_base_dir, min_length=10, max_length=15
):
    # Recursively go through all files in the folder
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".mp3") or filename.endswith(".wav"):  # Only process audio files
                file_path = os.path.join(root, filename)
                
                # Create a unique output directory for each audio file
                relative_path = os.path.relpath(root, input_folder)
                output_dir = os.path.join(output_base_dir, relative_path, os.path.splitext(filename)[0])
                
                # Call split_audio_at_lowest_frequency for each file
                split_audio_at_lowest_frequency(
                    file_path, output_dir, min_length, max_length
                )