# Coverts the videos to MP3 using ffmpeg and saves them in the output directory.
import os
import subprocess

files = os.listdir("Videos")

for file in files:
    file_name = file.removeprefix("0").removesuffix(".mp4")
    print(file_name)
    subprocess.run(["ffmpeg", "-i", f"Videos/{file}", f"Audios/{file_name}.mp3"])