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

Edit `.env` and set `OPENAI_API_KEY` for real responses. If not set, the API
returns a mock summary for testing.

### Run

```bash
uvicorn app.main:app --reload --app-dir backend
```

### Test

```bash
curl -X POST http://127.0.0.1:8000/summarize \
	-H "Content-Type: application/json" \
	-d '{"video_url":"https://www.youtube.com/watch?v=VIDEO_ID"}'
```

### Notes
- Transcript retrieval and Google STT are placeholders. Wire real services next.
- Responses are cached in memory by `video_id` and `include_english`.
