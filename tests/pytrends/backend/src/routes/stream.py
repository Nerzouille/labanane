"""
GET /stream?keyword=<keyword>  →  text/event-stream

Streams SSE events produced by the pipeline orchestrator.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from src.pipeline.orchestrator import run_pipeline

router = APIRouter()


@router.get("/stream")
async def stream(keyword: str = Query(..., min_length=1, description="Search keyword")):
    return StreamingResponse(
        run_pipeline(keyword),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
