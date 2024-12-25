import os
import json
from ffmpeg import probe
from pymediainfo import MediaInfo
from pprint import pprint
from moviepy.editor import VideoFileClip


class META:
    def __init__(self, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"The file '{path}' does not exist.")
        self.path = path

    def meta_data_extract(self):
        try:
            # Extract metadata from the file
            result = probe(self.path)["streams"]
            # Write metadata to a file in JSON format
            with open("result.txt", mode="a", encoding="utf-8") as data:
                json.dump(result, data, indent=4)
                data.write("\n")  # Add a newline for readability
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def mediainfo_ext(self):
        media_info = MediaInfo.parse(self.path)
        for track in media_info.tracks:
            if track.track_type == "Video":
                return track.to_data()
            elif track.track_type == "Audio":
                return track.to_data()
        os.remove(self.path)

    def ext_audio(self):
        output_dir = "audio"
        output_file = os.path.join(output_dir, "output_audio.mp3")
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        try:
            clip = VideoFileClip(self.path)
            # Write the audio file with the codec specified
            clip.audio.write_audiofile(output_file, codec="libmp3lame", bitrate="320k")
            clip.close()
            print(f"Audio extracted successfully: {output_file}")
            #os.remove(self.path)
        except Exception as e:
            print(f"An error occurred: {e}")
            os.remove(self.path)



    def split_video(self, output1, output2):
        # Load the video
        video = VideoFileClip(self.path)

        # Calculate the midpoint of the video
        midpoint = video.duration / 2

        # Split the video into two parts
        first_half = video.subclip(0, midpoint)
        second_half = video.subclip(midpoint, video.duration)

        # Save the two parts
        first_half.write_videofile(output1, codec="libx264", audio_codec="aac")
        second_half.write_videofile(output2, codec="libx264", audio_codec="aac")

        # Close the clips to free resources
        video.close()
        first_half.close()
        second_half.close()

    def trim_video(self, output_path, start_time, end_time):
        """
        Trims a video between the specified start and end times and saves it to a new file.

        Parameters:
            input_path (str): Path to the input video file.
            output_path (str): Path to save the trimmed video file.
            start_time (float): Start time in seconds.
            end_time (float): End time in seconds.

        Returns:
            None
        """
        try:
            # Load the video file
            clip = VideoFileClip(self.path)
            
            # Ensure start and end times are within the video duration
            if start_time < 0 or end_time > clip.duration or start_time >= end_time:
                raise ValueError("Invalid start_time or end_time.")
            
            # Trim the video
            trimmed_clip = clip.subclip(start_time, end_time)
            
            # Save the trimmed video to the output file
            trimmed_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            print(f"Video trimmed successfully and saved to {output_path}.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Clean up resources
            clip.close()




"""v1 = META(
    path="F:\Download\Desafio dos Jurados com a música Whenever, Wherever da Shakira - CANTA COMIGO.mp4"
)
v1.mediainfo_ext()
v1.ext_audio()"""
