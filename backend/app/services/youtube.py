from __future__ import annotations

from urllib.parse import parse_qs, urlparse


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
    """
    Placeholder transcript retriever.
    Returns (transcript_text, source).
    """
    return (
        "This is a placeholder transcript for video " + video_id + ".",
        "captions",
    )
