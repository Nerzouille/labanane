"""
Pipeline orchestrator.
Streams SSE events for a given keyword by calling all data sources.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from src.models.sse import (
    ExportReadyEvent,
    GoogleTrendsEvent,
    MarketplaceProduct,
    MarketplaceProductsEvent,
    SourceUnavailableEvent,
    TrendsDataPoint,
    TrendsRegion,
    format_sse,
)
from src.pipeline.sources.trends import fetch_trends


async def run_pipeline(keyword: str) -> AsyncGenerator[str, None]:  # type: ignore[return]
    """
    Async generator that yields SSE-formatted strings for all pipeline stages.
    Clients connect via GET /stream?keyword=<keyword>.
    """

    # ------------------------------------------------------------------ #
    # 1. Google Trends  (synchronous pytrends → run in thread pool)
    # ------------------------------------------------------------------ #
    try:
        d = await asyncio.to_thread(fetch_trends, keyword)
        yield format_sse(
            "google_trends",
            GoogleTrendsEvent(
                keyword=keyword,
                interest=[TrendsDataPoint(**dp) for dp in d["interest"]],
                trend_pct=d["trend_pct"],
                seasonality=d["seasonality"],
                regions=[TrendsRegion(**r) for r in d["regions"]],
                top_market=d["top_market"],
                opportunity=d["opportunity"],
            ),
        )
    except Exception as exc:
        print(f"[trends ERROR] {type(exc).__name__}: {exc}")
        yield format_sse(
            "source_unavailable",
            SourceUnavailableEvent(source="google_trends", message=str(exc)),
        )

    # ------------------------------------------------------------------ #
    # 2. Marketplace products (stub)
    # ------------------------------------------------------------------ #
    yield format_sse(
        "marketplace_products",
        MarketplaceProductsEvent(
            source="amazon",
            keyword=keyword,
            products=[
                MarketplaceProduct(
                    title=f"Sample product for '{keyword}'",
                    price=29.99,
                    currency="USD",
                    rating=4.3,
                    reviews=128,
                ),
            ],
        ),
    )

    # ------------------------------------------------------------------ #
    # 3. Export ready (stub)
    # ------------------------------------------------------------------ #
    yield format_sse(
        "export_ready",
        ExportReadyEvent(download_url=f"/exports/{keyword.replace(' ', '_')}.csv"),
    )


def get_report(keyword: str) -> dict:
    """Synchronous helper kept for testing / scripts."""
    import asyncio as _asyncio

    async def _collect() -> list[str]:
        return [chunk async for chunk in run_pipeline(keyword)]

    return {"frames": _asyncio.run(_collect())}
