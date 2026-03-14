from __future__ import annotations


def transcribe_audio_stub(video_id: str) -> tuple[str, str]:
    """
    Placeholder speech-to-text fallback.
    Returns (transcript_text, source).
    """
    return (
        "This is a placeholder STT transcript for video " + video_id + ".",
        "stt",
    )
