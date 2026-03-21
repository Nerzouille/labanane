"""
Pydantic models for all SSE event payloads.
Each event type maps to a named SSE event (event: <name>).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_sse(event_name: str, payload: BaseModel) -> str:
    """Serialise a Pydantic model as a named SSE frame."""
    return f"event: {event_name}\ndata: {payload.model_dump_json()}\n\n"


# ---------------------------------------------------------------------------
# Generic / error events
# ---------------------------------------------------------------------------

class SourceUnavailableEvent(BaseModel):
    status: Literal["unavailable"] = "unavailable"
    source: str
    message: str


# --- google_trends event ---

class TrendsDataPoint(BaseModel):
    date: str   # ISO date string e.g. "2024-03-10"
    value: int  # 0-100


class TrendsRegion(BaseModel):
    name: str
    value: int  # 0-100


class GoogleTrendsEvent(BaseModel):
    status: Literal["complete"] = "complete"
    keyword: str
    interest: list[TrendsDataPoint]
    trend_pct: int      # e.g. 34 for "+34%"
    seasonality: str    # e.g. "Oct"
    regions: list[TrendsRegion]
    top_market: str
    opportunity: str


# --- export_ready event ---

class ExportReadyEvent(BaseModel):
    status: Literal["ready"] = "ready"
    download_url: str


# --- marketplace_products event ---

class MarketplaceProduct(BaseModel):
    title: str
    price: float
    currency: str = "USD"
    rating: float | None = None
    reviews: int | None = None
    url: str | None = None


class MarketplaceProductsEvent(BaseModel):
    status: Literal["complete"] = "complete"
    source: str
    keyword: str
    products: list[MarketplaceProduct]
