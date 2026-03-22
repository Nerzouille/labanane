"""REST export endpoints: GET /api/export/{run_id}/markdown and /pdf."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from src.store import _reports
from src.logic.export import render_pdf

router = APIRouter(prefix="/api/export")


@router.get("/{run_id}/markdown")
async def export_markdown(run_id: str) -> Response:
    markdown = _reports.get(run_id)
    if markdown is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="analysis-{run_id}.md"'
        },
    )


@router.get("/{run_id}/pdf")
async def export_pdf(run_id: str) -> Response:
    markdown = _reports.get(run_id)
    if markdown is None:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = render_pdf(markdown)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="analysis-{run_id}.pdf"'
        },
    )
