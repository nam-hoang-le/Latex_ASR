import os
import json
from google.oauth2 import service_account
from google.cloud import speech
from pydub import AudioSegment

# Function to create authentication credentials
def get_credentials(credentials_path):
    credentials_path = credentials_path
    return service_account.Credentials.from_service_account_file(credentials_path)

# Function to extract a small audio sample from the audio file
def get_audio_sample(audio_file):
    audio = AudioSegment.from_file(audio_file)
    duration = len(audio) / 1000.0  # Convert milliseconds to seconds
    sample_rate_hertz = audio.frame_rate

    # Extract 1/100 of the audio file as a sample
    sample_duration = duration / 100  # 1% of total duration
    sample = audio[: int(sample_duration * 1000)]  # pydub uses milliseconds

    return sample, duration, sample_rate_hertz

# Function to transcribe the audio sample using Google Cloud Speech-to-Text
def transcribe_audio_sample(client, audio_sample, sample_rate_hertz):
    audio_content = audio_sample.raw_data
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return " ".join(result.alternatives[0].transcript for result in response.results)

# Function to transcribe an entire audio file
def transcribe_audio(audio_file):
    credentials = get_credentials()
    client = speech.SpeechClient(credentials=credentials)

    # Get a sample from the audio file, duration, and sample rate
    audio_sample, duration, sample_rate_hertz = get_audio_sample(audio_file)

    # Transcribe the sample
    transcript = transcribe_audio_sample(client, audio_sample, sample_rate_hertz)

    return transcript, duration, sample_rate_hertz

# Function to process all .mp3 files in a nested folder structure and save results to a JSON file
def process_all_audios(input_folder, output_json):
    results = []

    # Recursively search through all subdirectories
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".mp3"):  # Only process .mp3 files
                audio_path = os.path.join(root, filename)
                print(f"Processing file: {filename}")

                # Transcribe audio and get metadata
                transcript, duration, sample_rate_hertz = transcribe_audio(audio_path)

                # Store data in dictionary format
                audio_data = {
                    "filename": filename,
                    "path": audio_path,  # Store full path for reference
                    "transcript": transcript,
                    "duration": duration,
                    "sample_rate_hertz": sample_rate_hertz,
                }
                results.append(audio_data)

    # Write results to the JSON file
    with open(output_json, "w") as f:
        json.dump(results, f, indent=4)