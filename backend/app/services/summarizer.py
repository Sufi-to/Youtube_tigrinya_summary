from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.config import Settings
from app.models import ImportantTerm, SummaryPayload


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
        "Return strict JSON with keys: topic, short_summary_ti, key_points_ti, "
        "important_terms_ti (list of {term, explanation}). "
        "Write natural, clear Tigrinya, not literal translation. "
        f"{extra}\n\nTranscript:\n{transcript}"
    )


def summarize_transcript(
    transcript: str,
    settings: Settings,
    include_english: bool,
) -> SummaryPayload:
    if settings.mock_mode:
        return _mock_summary()

    client = OpenAI(api_key=settings.openai_api_key)

    chunks = _chunk_text(transcript, settings.chunk_size_words)
    if len(chunks) == 1:
        prompt = _build_prompt(chunks[0], include_english)
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        payload = json.loads(response.choices[0].message.content)
        return _parse_payload(payload, include_english)

    # Summarize each chunk in English, then summarize the combined result.
    chunk_summaries = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "Summarize this transcript chunk in English.",
                },
                {"role": "user", "content": chunk},
            ],
            temperature=0.2,
        )
        chunk_summaries.append(response.choices[0].message.content)

    combined = "\n".join(chunk_summaries)
    final_prompt = _build_prompt(combined, include_english)
    final_response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.2,
    )
    payload = json.loads(final_response.choices[0].message.content)
    return _parse_payload(payload, include_english)
