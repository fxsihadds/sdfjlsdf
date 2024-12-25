from PIL import Image
from random import randint
from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
from random import randint

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def get_video_duration(video_file_path):
    try:
        with VideoFileClip(video_file_path) as video_clip:
            duration = int(video_clip.duration)
        return duration
    except Exception as e:
        print(f"Error: {e}")
        return None


def thumbnail_video(video_file_path):
    duration = get_video_duration(video_file_path)
    rnm = str(randint(0, duration))
    try:
        with VideoFileClip(video_file_path) as video_clip:
            thumbnail_frame = video_clip.get_frame(rnm)
            thumbnail_image = Image.fromarray(thumbnail_frame)
            thumb_path = f'{randint(1,100)}thumbnail.png'
            thumb = thumbnail_image.save(thumb_path)
    except Exception as e:
        print(f"Error: {e}")
    else:
        return thumb_path


def split_scene(video_file_path) -> bool:
    if os.path.isfile(video_file_path):
        get_size = os.path.getsize(video_file_path)
        file_size_megabytes = round(get_size / (1024 * 1024))
        print(f"File size: {file_size_megabytes} MB")
        if file_size_megabytes > 4000:
            durations = get_video_duration(video_file_path)
            num_segments = 2
            segment_duration = durations / num_segments
            output_directory = "your_download"
            os.makedirs(output_directory, exist_ok=True)

            for i in range(num_segments):
                start_time = i * segment_duration
                end_time = (i + 1) * segment_duration
                output_file = os.path.join(
                    output_directory, f"{os.path.basename(video_file_path)}_{i + 1}.mp4")

                with open(video_file_path, 'rb') as video_file:
                    ffmpeg_extract_subclip(
                        video_file_path, start_time, end_time, targetname=output_file)

            print("Video split into segments.")
            os.remove(video_file_path)
            return True
        else:
            return False
            print("File is small enough to upload to Telegram.")
    else:
        return False
        print("File not found.")


def get_file_size(video_file_path) -> bool:
    get_size = os.path.getsize(video_file_path)
    file_size_megabytes = round(get_size / (1024 * 1024))
    print(f"File size: {file_size_megabytes} MB")
    if file_size_megabytes < 4000:
        return True
    else:
        os.remove(video_file_path)
        return False
