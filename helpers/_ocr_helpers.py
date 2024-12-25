import time
import subprocess
import os
import zipfile
from helpers.timemanager import create_task_for_user, run_sync_in_thread
import shutil


# This functions Work only for Windows Rdp, I try to fix It,
# there is an issue for binnary file execution

@run_sync_in_thread
def sub_images(bot, status, video_path, tmp_dir):
    try:
        status.edit_text(
            "Extracting subtitle images with VideoSubFinder (takes quite a long time) ...")

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        startTime = time.time()
        subprocess.run([
            "C:/Users/Shovo/Downloads/VideoSubFinder_5.40_x64/Release_x64/VideoSubFinderWXW.exe",
            "--clear_dirs",
            "--run_search",
            "--create_cleared_text_images",
            "--input_video", video_path,
            "--output_dir", tmp_dir,
            "--num_threads", str(4),
            "--num_ocr_threads", str(4),
            "--top_video_image_percent_end", str(0.25),
            "--bottom_video_image_percent_end", str(0.0)
        ], capture_output=True)

        endTime = time.time()
        status.edit_text(f"Completed! Took {round(endTime - startTime)}s")

        output_zip = "images.zip"
        output_folder = f'{tmp_dir}/RGBImages'
        zip_output(output_zip, output_folder)

        with open(output_zip, "rb") as zip_file:
            bot.send_document(
                chat_id=status.chat.id,
                document=zip_file,
                caption="Output"
            )

        os.remove(output_zip)
        shutil.rmtree(tmp_dir)

    except Exception as e:
        status.edit_text(f"Error in sub_images: {e}")


def zip_output(zip_file_name, source_dir):
    with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(
                    os.path.join(root, file), source_dir))
