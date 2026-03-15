from __future__ import annotations

import logging
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname in {"www.youtube.com", "youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/")[1].split("/")[0]
            return video_id or None
        query = parse_qs(parsed.query)
        return query.get("v", [None])[0]
    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/") or None
    return None


def get_video_title(video_id: str) -> str | None:
    try:
        with YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
            return info.get("title") if info else None
    except Exception:
        logger.warning("Failed to fetch video title for %s", video_id)
        return None


def get_transcript(video_id: str) -> tuple[str | None, str]:
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id=video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        logger.info("Captions unavailable for video %s", video_id)
        return (None, "captions-unavailable")
    except Exception:
        logger.warning("Unexpected error fetching transcript for %s", video_id, exc_info=True)
        return (None, "captions-error")

    text = " ".join(snippet.text for snippet in transcript.snippets).strip()
    return (text, "captions")
