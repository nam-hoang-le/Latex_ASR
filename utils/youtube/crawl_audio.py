import yt_dlp
import re
import os
import json

def convert_to_playlist_url(url):
    """
    Converts a YouTube video URL with a playlist to the corresponding playlist URL.
    Removes any `&index=` part and converts "watch?v=" format to "playlist?list=" format.
    """
    url = re.sub(r"&index=\d*", "", url)
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    if match:
        playlist_id = match.group(1)
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    return url  # Return the original URL if it doesn't contain a playlist

def download_playlist_audios(playlist_urls, audio_folder, schools, titles, json_output_path):
    """
    Downloads audio files from a list of YouTube playlists and organizes them
    in a folder structure: audio_folder/School/Title/audio_X.mp3

    Args:
    playlist_urls (list): List of playlist URLs.
    audio_folder (str): Base directory to save the downloaded audio files.
    schools (list): List of schools for organizing folder structure.
    titles (list): List of course titles for organizing folder structure.
    json_output_path (str): Path to save the output JSON mapping file.
    """
    
    # Dictionary to store mappings for JSON
    audio_to_video_mapping = {}

    for idx, original_url in enumerate(playlist_urls):
        # Remove &index=, then convert video URL with playlist to a playlist URL
        playlist_url = convert_to_playlist_url(original_url)
        
        # Convert school and title to strings if they're not, handling potential float values
        school = str(schools[idx]) if schools[idx] is not None else ""
        title = str(titles[idx]) if titles[idx] is not None else ""
        
        # Sanitize school and title to remove invalid directory characters
        school = re.sub(r'[\\/*?:"<>|\n\r]', "", school.strip())
        title = re.sub(r'[\\/*?:"<>|\n\r]', "", title.strip())

        # Create the school and title directories if they don't exist
        course_folder = os.path.join(audio_folder, school, title)
        os.makedirs(course_folder, exist_ok=True)

        # Use yt_dlp to retrieve each video's URL in the playlist
        ydl_opts_playlist = {"quiet": True, "extract_flat": True, "skip_download": True}
        
        print(f"\nRetrieving videos from playlist: {playlist_url}")
        with yt_dlp.YoutubeDL(ydl_opts_playlist) as ydl:
            try:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                entries = playlist_info.get("entries", [])
                print(f"Found {len(entries)} videos in the playlist.")
            except Exception as e:
                print(f"Error retrieving playlist info: {e}")
                continue

        # Process each video in the playlist
        for i, video in enumerate(entries, start=1):
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            print(f"Processing video {i}: {video_url}")
            try:
                # Retrieve video title
                ydl_opts_info = {"quiet": True, "skip_download": True}
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    video_title = info.get("title", f"video_{i}").strip()
                    video_title_cleaned = re.sub(r'[\\/*?:"<>|\n\r]', "", video_title)  # Clean invalid characters
                
                # Construct audio file name and mapping key
                audio_file_name = f"audio_{i}.mp3"
                audio_path = os.path.join(course_folder, f"audio_{i}")
                audio_path_check = os.path.join(course_folder, audio_file_name)
                mapping_key = audio_path_check  # Full path including file extension
                mapping_value = f"{i}. {video_title_cleaned}"  # Title without prefix

                # Add to dictionary for JSON mapping (whether file exists or not)
                audio_to_video_mapping[mapping_key] = mapping_value

                # Check if audio file already exists
                if os.path.exists(audio_path_check):
                    print(f"File {audio_file_name} already exists, skipping download.")
                    continue  # Skip download if the file already exists

                # Download only the best available audio if not already downloaded
                ydl_opts_download = {
                    "format": "bestaudio/best",  # Download only audio
                    "outtmpl": audio_path,  # Set output path without extension
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",  # Extract audio using FFmpeg
                            "preferredcodec": "mp3",  # Convert to mp3
                            "preferredquality": "192",  # Audio quality
                        }
                    ],
                    "keepvideo": False,  # Discard video after extracting audio
                    "writethumbnail": False,
                    "writesubtitles": False,
                    "writeautomaticsub": False,
                }
                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.download([video_url])

            except Exception as e:
                print(f"Error processing video {video_url}: {e}")

    # Save mappings to JSON with paths as keys
    with open(json_output_path, "w", encoding="utf-8") as json_file:
        json.dump(audio_to_video_mapping, json_file, ensure_ascii=False, indent=4)

    print("Processing complete for all videos.")
