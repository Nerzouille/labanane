#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kill any processes still lingering on our ports
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true

# Start FastAPI backend
echo "Starting FastAPI backend on http://localhost:8000 ..."
cd "$SCRIPT_DIR/backend"
uv run uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Start SvelteKit frontend
echo "Starting SvelteKit frontend on http://localhost:5173 ..."
cd "$SCRIPT_DIR/frontend"
~/.bun/bin/bun install
~/.bun/bin/bun run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "  Backend:  http://localhost:8000/health"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
