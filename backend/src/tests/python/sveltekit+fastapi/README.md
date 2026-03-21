# SvelteKit + FastAPI SSE Demo

A demo project showing Server-Sent Events (SSE) streaming from a FastAPI backend through a SvelteKit BFF (Backend-for-Frontend) proxy to the browser.

## Architecture

```
Browser → SvelteKit (/api/sse) → FastAPI (/stream)
```

The SvelteKit server acts as a transparent proxy, forwarding the SSE stream from FastAPI to the browser. This avoids CORS issues and keeps the backend URL internal.

## Setup

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend (SvelteKit)

```bash
cd frontend
npm install
```

## Running

### Option 1: Use the run script

```bash
chmod +x run.sh
./run.sh
```

### Option 2: Run manually in separate terminals

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Usage

1. Open http://localhost:5173
2. Click "Start Stream"
3. Watch the progress bar fill up as SSE events arrive from the FastAPI backend (5 events, 1.5s apart)
