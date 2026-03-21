#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Backend ───────────────────────────────────────────────────────────────────
echo "Starting FastAPI backend on http://localhost:8000 ..."
cd "$SCRIPT_DIR/backend"

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt -q

uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# ── Frontend ──────────────────────────────────────────────────────────────────
echo "Starting SvelteKit frontend on http://localhost:5173 ..."
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    # Use bun if available, otherwise fallback to npm
    if command -v bun &>/dev/null; then
        bun install
    else
        npm install
    fi
fi

if command -v bun &>/dev/null; then
    bun run dev &
else
    npm run dev &
fi
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "Both services are running."
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
