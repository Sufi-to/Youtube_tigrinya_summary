from __future__ import annotations

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    video_url: str | None = None
    video_id: str | None = None
    force_refresh: bool = False
    include_english: bool = False


class ImportantTerm(BaseModel):
    term: str
    explanation: str


class SummaryPayload(BaseModel):
    topic: str
    short_summary_ti: str
    key_points_ti: list[str] = Field(default_factory=list)
    important_terms_ti: list[ImportantTerm] = Field(default_factory=list)

    short_summary_en: str | None = None
    key_points_en: list[str] | None = None
    important_terms_en: list[ImportantTerm] | None = None


class SummarizeResponse(BaseModel):
    video_id: str
    video_title: str | None = None
    transcript_source: str
    source: str
    processing_seconds: float
    summary: SummaryPayload
