from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname in {"www.youtube.com", "youtube.com"}:
        query = parse_qs(parsed.query)
        return query.get("v", [None])[0]
    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/") or None
    return None


def get_video_title(video_id: str) -> str | None:
    return None


def get_transcript(video_id: str) -> tuple[str | None, str]:
    try:
        items = YouTubeTranscriptApi.get_transcript(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return (None, "captions-unavailable")

    text = " ".join(item.get("text", "") for item in items).strip()
    return (text, "captions")
