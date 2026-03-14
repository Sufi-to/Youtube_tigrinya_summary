from __future__ import annotations

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import SummarizeRequest, SummarizeResponse
from app.services.cache import InMemoryCache
from app.services.summarizer import summarize_transcript
from app.services.stt import transcribe_audio_stub
from app.services.youtube import extract_video_id, get_transcript, get_video_title


app = FastAPI(title="YouTube Tigrinya Summarizer API")
settings = get_settings()
cache = InMemoryCache()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(payload: SummarizeRequest) -> SummarizeResponse:
    start = time.monotonic()

    video_id = payload.video_id
    if not video_id and payload.video_url:
        video_id = extract_video_id(payload.video_url)

    if not video_id:
        raise HTTPException(status_code=400, detail="video_id or video_url required")

    cache_key = f"summary:{video_id}:en={payload.include_english}"
    if not payload.force_refresh:
        cached = cache.get(cache_key)
        if cached:
            cached.processing_seconds = round(time.monotonic() - start, 3)
            return cached

    transcript, source = get_transcript(video_id)
    if not transcript:
        transcript, source = transcribe_audio_stub(video_id)

    summary = summarize_transcript(
        transcript=transcript,
        settings=settings,
        include_english=payload.include_english,
    )

    response = SummarizeResponse(
        video_id=video_id,
        video_title=get_video_title(video_id),
        transcript_source=source,
        source="fresh",
        processing_seconds=round(time.monotonic() - start, 3),
        summary=summary,
    )

    cache.set(cache_key, response, settings.cache_ttl_seconds)
    return response
