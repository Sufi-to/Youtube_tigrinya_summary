from __future__ import annotations

import glob
import logging
import os
import tempfile
from typing import Any

import whisper
from yt_dlp import YoutubeDL

from app.config import Settings

logger = logging.getLogger(__name__)

_WHISPER_MODEL: Any | None = None
_WHISPER_MODEL_NAME: str | None = None


def _get_whisper_model(model_name: str):
    global _WHISPER_MODEL, _WHISPER_MODEL_NAME
    if _WHISPER_MODEL is None or _WHISPER_MODEL_NAME != model_name:
        logger.info("Loading Whisper model: %s", model_name)
        _WHISPER_MODEL = whisper.load_model(model_name)
        _WHISPER_MODEL_NAME = model_name
    return _WHISPER_MODEL


def _download_audio(video_url: str, output_dir: str) -> str:
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    matches = glob.glob(os.path.join(output_dir, "audio.*"))
    if not matches:
        raise RuntimeError("Audio download failed.")
    return matches[0]


def transcribe_video_audio(video_url: str, settings: Settings) -> tuple[str, str]:
    logger.info("Starting audio transcription for %s", video_url)
    with tempfile.TemporaryDirectory() as tmp_dir:
        audio_path = _download_audio(video_url, tmp_dir)
        logger.info("Audio downloaded to %s", audio_path)
        model = _get_whisper_model(settings.whisper_model)
        result = model.transcribe(audio_path, language=settings.whisper_language)
        text = result.get("text", "").strip()
        logger.info("Transcription complete: %d characters", len(text))
        return (text, "whisper")
