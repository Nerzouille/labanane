# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A demo of SSE streaming through a SvelteKit BFF (Backend-for-Frontend) proxy to a FastAPI backend. The browser never talks to FastAPI directly.

```
Browser → EventSource('/api/sse') → SvelteKit server → fetch('http://localhost:8000/stream') → FastAPI
```

## Commands

### Run both services
```bash
./run.sh
```

### Backend
```bash
cd backend
python -m venv .venv          # first time only
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test the stream directly:
```bash
curl http://localhost:8000/stream
curl http://localhost:8000/health
```

### Frontend
```bash
cd frontend
npm install                   # first time only
npm run dev                   # http://localhost:5173
npm run check                 # svelte-check type checking
npm run build                 # production build
```

## Architecture

### Data flow
1. FastAPI `event_generator()` yields `SSEPayload` Pydantic models as `data: <json>\n\n`
2. SvelteKit `GET /api/sse` fetches the upstream, pipes the raw byte stream back to the browser
3. Browser `EventSource` receives events; `createSSEStream()` validates each payload with Zod before calling callbacks
4. The Svelte component updates reactive state and re-renders

### Backend modules (`backend/`)
- `config.py` — `pydantic-settings` config; all settings overridable via `APP_*` env vars or `backend/.env`
- `models.py` — Pydantic models: `SSEPayload` (normal events) and `SSEErrorPayload` (emitted on generator exceptions as `event: error`)
- `routes/stream.py` — the only route; `GET /stream` returns a `StreamingResponse`
- `main.py` — app factory: mounts the router, adds CORS middleware, exposes `GET /health`

### Frontend modules (`frontend/src/`)
- `lib/types.ts` — Zod schema (`SSEPayloadSchema`) and inferred types (`SSEPayload`, `ConnectionState`). Single source of truth for the event shape.
- `lib/sse.ts` — `createSSEStream(url, callbacks)` abstraction: opens `EventSource`, validates with Zod, distinguishes named `event: error` server events from connection-drop errors, returns a cleanup function
- `routes/api/sse/+server.ts` — SvelteKit server route that proxies the FastAPI stream; handles backend-unreachable (502) gracefully
- `routes/+page.svelte` — Svelte 5 runes component using `$state`, `$derived`, `$effect`, `onclick`

### Svelte 5 / svelte-check note
svelte-check 4.4.5 has a bug: the `$state()` rune is only recognized as a rune (not a store subscription) when the variable name contains the string `'state'` (case-sensitive). The workaround used throughout the page component is a **single `let state = $state({...})` object** that holds all reactive values (`conn`, `progress`, `currentTask`, `errorMsg`, `events`). This produces zero svelte-check errors while keeping full Svelte 5 rune syntax.

### Configuration
Backend settings (all optional, env prefix `APP_`):

| Variable | Default | Description |
|---|---|---|
| `APP_EVENT_COUNT` | `5` | Number of SSE events to emit per stream |
| `APP_EVENT_INTERVAL` | `1.5` | Seconds between events |
| `APP_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |

The SvelteKit proxy backend URL is hardcoded in `frontend/src/routes/api/sse/+server.ts` as `http://localhost:8000/stream`.
