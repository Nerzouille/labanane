# Quickstart: Market Intelligence AI — Hackathon MVP

**Branch**: `001-market-intelligence-mvp` | **Date**: 2026-03-21

---

## Prerequisites

- Python 3.12+ with `uv` installed (`pip install uv` or `curl -Lsf https://astral.sh/uv/install.sh | sh`)
- Bun installed (`curl -fsSL https://bun.sh/install | bash`)
- An OpenAI API key (for LLM analysis sections)

---

## Environment Setup

**Backend** — create `backend/.env`:
```env
APP_OPENAI_API_KEY=sk-...
APP_LLM_MODEL=gpt-4o-mini
APP_CORS_ORIGINS=["http://localhost:5173"]
APP_SOURCE_TIMEOUT=10
```

**Frontend** — create `frontend/.env`:
```env
PUBLIC_API_BASE=http://localhost:8000
```

---

## Running the Application

From the repository root:
```bash
chmod +x run.sh
./run.sh
```

This starts:
- FastAPI backend at `http://localhost:8000`
- SvelteKit frontend at `http://localhost:5173`

Open `http://localhost:5173` in your browser.

---

## Manual Startup (if run.sh fails)

**Backend**:
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload --port 8000
```

**Frontend** (in a second terminal):
```bash
cd frontend
bun install
bun run dev
```

---

## Validating the Setup

1. Open `http://localhost:5173`
2. Enter `eco-friendly bamboo skincare` in the search field
3. Click **Analyse**
4. Verify:
   - Amazon products appear within 5 seconds
   - Dashboard sections build progressively (skeleton → streaming → complete)
   - Viability score renders with explanation
   - Target persona, differentiation angles, competitive overview appear in sequence
   - Export buttons appear when analysis completes
5. Click **Export Markdown** — verify download contains `Score: {n}/100` on its own line
6. Click **New analysis** — verify page resets immediately to input state

---

## Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

---

## Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/stream?keyword={kw}` | GET | Main SSE stream (via BFF: `/api/sse?keyword={kw}`) |
| `/export/md?keyword={kw}` | GET | Markdown export download |
| `/export/pdf?keyword={kw}` | GET | PDF export download |

---

## Troubleshooting

**Amazon returns no products**: Amazon bot-detection may block scraping. The
pipeline will emit `source_unavailable` and continue. The analysis will be
partial but functional.

**LLM sections never complete**: Verify `APP_OPENAI_API_KEY` is set correctly.
Check backend logs for OpenAI API errors.

**Frontend shows blank page**: Ensure bun dependencies are installed (`bun install`
inside `frontend/`). Check browser console for errors.

**Port conflicts**: Edit `run.sh` to change ports if 8000 or 5173 are in use.
Update `APP_CORS_ORIGINS` and `PUBLIC_API_BASE` accordingly.
