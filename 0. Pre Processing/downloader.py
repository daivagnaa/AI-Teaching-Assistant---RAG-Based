# Download complete playlist from YouTube using yt-dlp
from __future__ import annotations

import os
import sys
import importlib
from pathlib import Path

try:
	YoutubeDL = importlib.import_module("yt_dlp").YoutubeDL
except ImportError as exc:
	raise SystemExit(
		"Missing dependency: yt-dlp. Install it with: pip install yt-dlp"
	) from exc


PLAYLIST_URL = (
	"https://youtube.com/playlist?list=PLGMBjWR7dGL_XFUbQQhJIaojuDhWF35yk&si=rbEdCBoDZESwB7Ta"
)
DOWNLOAD_DIR = Path(__file__).resolve().parent / "Videos"


def download_playlist(url: str) -> None:
	DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

	ydl_options = {
		"format": "best[ext=webm][vcodec!=none][acodec!=none]/best[ext=mp4][vcodec!=none][acodec!=none]/best[acodec!=none][vcodec!=none]",
		"outtmpl": os.path.join(
			str(DOWNLOAD_DIR),
			"%(playlist_title).200s",
			"%(playlist_index)03d - %(title).200s.%(ext)s",
		),
		"noplaylist": False,
		"ignoreerrors": True,
		"retries": 5,
		"continuedl": True,
		"windowsfilenames": True,
		"quiet": False,
		"no_warnings": False,
	}

	with YoutubeDL(ydl_options) as ydl:
		ydl.download([url])


def main() -> None:
	url = sys.argv[1] if len(sys.argv) > 1 else PLAYLIST_URL
	download_playlist(url)


if __name__ == "__main__":
	main()
