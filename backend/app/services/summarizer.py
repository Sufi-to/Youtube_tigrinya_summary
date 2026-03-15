from __future__ import annotations

import json
import logging
from typing import Any

import requests

from app.config import Settings
from app.models import ImportantTerm, SummaryPayload

logger = logging.getLogger(__name__)


def _chunk_text(text: str, chunk_size_words: int) -> list[str]:
    words = text.split()
    if len(words) <= chunk_size_words:
        return [text]
    chunks = []
    for i in range(0, len(words), chunk_size_words):
        chunks.append(" ".join(words[i : i + chunk_size_words]))
    return chunks


def _mock_summary() -> SummaryPayload:
    return SummaryPayload(
        topic="Sample Topic",
        short_summary_ti="እዚ ናይ መርኣያ ሓጺር ሓሳብ እዩ።",
        key_points_ti=[
            "እቲ ቪድዮ ዋና ጉዳይ ንዘርከበ።",
            "ኣርእስቱ ብምክንያት ተጠቃሚ እዩ።",
        ],
        important_terms_ti=[
            ImportantTerm(term="ሓሳብ", explanation="ኣስተዋጽኦ ኣድላይ ሓሳብ ምሕባር"),
        ],
    )


def _parse_payload(payload: dict[str, Any], include_english: bool) -> SummaryPayload:
    summary = SummaryPayload(
        topic=payload.get("topic", ""),
        short_summary_ti=payload.get("short_summary_ti", ""),
        key_points_ti=payload.get("key_points_ti", []),
        important_terms_ti=[
            ImportantTerm(**term)
            for term in payload.get("important_terms_ti", [])
            if isinstance(term, dict)
        ],
    )

    if include_english:
        summary.short_summary_en = payload.get("short_summary_en")
        summary.key_points_en = payload.get("key_points_en")
        summary.important_terms_en = [
            ImportantTerm(**term)
            for term in payload.get("important_terms_en", [])
            if isinstance(term, dict)
        ]

    return summary


def _build_prompt(transcript: str, include_english: bool) -> str:
    extra = (
        "Include English fields: short_summary_en, key_points_en, important_terms_en."
        if include_english
        else ""
    )
    return (
        "You are a helpful assistant that summarizes YouTube transcripts. "
        "Return ONLY valid JSON with no extra text. Keys: topic, short_summary_ti, key_points_ti, "
        "important_terms_ti (list of {term, explanation}). "
        "Write natural, clear Tigrinya, not literal translation. "
        f"{extra}\n\nTranscript:\n{transcript}"
    )


def _extract_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise
        return json.loads(text[start : end + 1])


def _ollama_chat(
    settings: Settings,
    messages: list[dict[str, str]],
    json_mode: bool = False,
) -> str:
    body: dict[str, Any] = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
    }
    if json_mode:
        body["format"] = "json"

    response = requests.post(
        f"{settings.ollama_base_url}/api/chat",
        json=body,
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["message"]["content"]


def summarize_transcript(
    transcript: str,
    settings: Settings,
    include_english: bool,
) -> SummaryPayload:
    if settings.mock_mode:
        return _mock_summary()

    chunks = _chunk_text(transcript, settings.chunk_size_words)
    logger.info("Transcript split into %d chunk(s)", len(chunks))

    if len(chunks) == 1:
        prompt = _build_prompt(chunks[0], include_english)
        content = _ollama_chat(
            settings,
            [
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )
        payload = _extract_json(content)
        return _parse_payload(payload, include_english)

    # Summarize each chunk in English, then summarize the combined result.
    chunk_summaries = []
    for idx, chunk in enumerate(chunks, 1):
        logger.info("Summarizing chunk %d/%d", idx, len(chunks))
        content = _ollama_chat(
            settings,
            [
                {
                    "role": "system",
                    "content": "Summarize this transcript chunk in English.",
                },
                {"role": "user", "content": chunk},
            ],
        )
        chunk_summaries.append(content)

    combined = "\n".join(chunk_summaries)
    final_prompt = _build_prompt(combined, include_english)
    final_content = _ollama_chat(
        settings,
        [
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": final_prompt},
        ],
        json_mode=True,
    )
    payload = _extract_json(final_content)
    return _parse_payload(payload, include_english)
