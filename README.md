# Youtube_tigrinya_summary
This project builds a FastAPI backend for a YouTube-to-Tigrinya summarizer.

## Backend (local dev)

### Setup
1) Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2) Configure environment variables:

```bash
cp backend/.env.example .env
```

Edit `.env` and set Ollama + Whisper configuration. The API uses Ollama for
summaries by default; use `USE_MOCK_SUMMARY=true` for mock responses.

### Run

```bash
uvicorn app.main:app --reload --app-dir backend
```

### Ollama + Whisper prerequisites

1) Install and run Ollama, then pull the model:

```bash
ollama serve
ollama pull qwen3.5:27b
```

2) Install FFmpeg for audio extraction (required by `yt-dlp` + Whisper).

### Test

```bash
curl -X POST http://127.0.0.1:8000/summarize \
	-H "Content-Type: application/json" \
	-d '{"video_url":"https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Notes
- Transcript retrieval uses YouTube captions when available.
- Whisper is used locally for speech-to-text fallback.
- Responses are cached in memory by `video_id` and `include_english`.
