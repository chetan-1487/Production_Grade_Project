import os
import uuid
from yt_dlp import YoutubeDL
from datetime import datetime
from typing import Dict, Tuple, Optional
from app.Core.celery_worker.celery_worker import celery_app
from celery import shared_task
from fastapi import HTTPException
from ...Core.config import MAX_DURATION,MAX_SIZE
import subprocess

# Mapping of quality labels to video height (used by yt_dlp for filterin
QUALITY_MAP = {
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "4k": 2160
}

# Save to Desktop/Downloads
# Set base download directory to the user's Downloads folder
# BASE_DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
# os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)
BASE_DOWNLOAD_DIR = '/home/chetan/Downloads'  # Host machine Downloads folder
os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)


# Define a Celery task for downloading videos (supports individual videos or playlists)
# @celery_app.task(name="app.Core.Service.download.download_video")
@shared_task
def download_video(url: str, quality: str = '1080p', file_format: str = 'mp4', start_time: Optional[str] = None, end_time: Optional[str]=None) -> list:  #tuple
    extension = "mp3" if file_format == "mp3" else file_format
    output_path = os.path.join(BASE_DOWNLOAD_DIR, f"%(id)s.%(ext)s")
    result=[]

    # Define yt_dlp options based on file format
    if file_format == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': False,
            'quiet': True,
            'playlistend': 10,
        }
    else:
        if quality not in QUALITY_MAP:
            raise RuntimeError(f"Invalid quality value: {quality}. Must be 360p, 480p, 720p, 1080p, 4K etc.")
    
        int_quality = QUALITY_MAP[quality]

        # Define format string for video + audio merge
        format_string = (
            f"bestvideo[height<={int_quality}][ext={file_format}]+"
            f"bestaudio[ext=m4a]/best[ext={file_format}]/best"
        )

        # Download video with given constraints
        ydl_opts = {
            'format': format_string,
            'outtmpl': output_path,
            'merge_output_format': file_format,
            'noplaylist': False,
            'quiet': True,
            'playlistend': 10,
        }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading to validate duration & size
            check = ydl.extract_info(url, download=False)
            if not check:
                raise RuntimeError("Failed to extract video information.")
            

            try:
                max_duration = MAX_DURATION
                max_size = MAX_SIZE
            except ValueError:
                raise RuntimeError("Environment variables MAX_DURATION or MAX_SIZE must be integers")
            filesize = check.get("filesize") or 0
            duration = check.get("duration") or 0

            # Validate duration
            if duration > max_duration:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video duration exceeds 5 hours. (Got {duration // 3600}h {duration % 3600 // 60}m)"
                )

            # Validate file size
            if filesize > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video file size exceeds 3 GB. (Got {filesize / (1024**3):.2f} GB)"
                )
            # Proceed with download
            info = ydl.extract_info(url, download=True)
            if not info:
                raise RuntimeError("Failed to extract video information.")
            
            # Support for playlists and single video
            entries=info.get("entries",[])
            if not entries:
                entries=[info]
            
            for entry in entries:

                original_id = entry.get("id")
                original_file_path = os.path.join(BASE_DOWNLOAD_DIR, f"{original_id}.{extension}")
                final_file_path = original_file_path

                # If trimming requested
                if start_time and end_time:
                    trimmed_file_path = os.path.join(BASE_DOWNLOAD_DIR, f"{uuid.uuid4()}.{extension}")
                    try:
                        ffmpeg_cmd = [
                            "ffmpeg", "-y",
                            "-i", original_file_path,
                            "-ss", start_time,
                            "-to", end_time,
                            "-c", "copy",
                            trimmed_file_path
                        ]
                        subprocess.run(ffmpeg_cmd, check=True)
                        os.remove(original_file_path)
                        final_file_path = trimmed_file_path
                    except Exception as e:
                        raise RuntimeError(f"Trimming failed: {str(e)}")


                video_id = str(uuid.uuid4())
                file_path = os.path.join(BASE_DOWNLOAD_DIR, f"{video_id}.{extension}")

                # Prepare video metadata
                metadata = {
                    "id": video_id,
                    "title": entry.get("title"),
                    "duration": format_duration(entry.get("duration", 0)),
                    "views": entry.get("view_count", 0),
                    "likes": entry.get("like_count", 0),
                    "channel": entry.get("uploader"),
                    "thumbnail_url": entry.get("thumbnail"),
                    "published_date": datetime.strptime(entry.get("upload_date", "19700101"), "%Y%m%d").date()
                }

                # Append result (for each video in playlist or single)
                result.append((file_path, metadata))

        return result
    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")

# Utility function to format seconds into "XmYs"
def format_duration(seconds: int) -> str:
    mins, secs = divmod(seconds, 60)
    return f"{mins}m{secs}s"