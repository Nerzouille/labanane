"""
Google Trends data fetcher using pytrends.
Returns structured data for use in the SSE pipeline.

Set TRENDS_MOCK=1 (env var) to bypass the real API and use generated mock data.
Useful when Google rate-limits (429) during dev.
"""

from __future__ import annotations

import datetime
import math
import os
import random
from typing import Any

from pytrends.request import TrendReq

_MOCK = os.getenv("TRENDS_MOCK", "0") == "1"


def _mock_trends(keyword: str) -> dict[str, Any]:
    """Generate plausible-looking mock data for UI development."""
    rng = random.Random(hash(keyword) & 0xFFFFFFFF)
    today = datetime.date.today()
    # 52 weekly points going back 1 year
    interest = []
    base = rng.randint(30, 60)
    for i in range(52):
        d = today - datetime.timedelta(weeks=51 - i)
        noise = rng.randint(-8, 8)
        wave = int(12 * math.sin(i / 52 * 2 * math.pi))
        val = max(0, min(100, base + wave + noise + i // 8))
        interest.append({"date": str(d), "value": val})

    values = [p["value"] for p in interest]
    avg_last = sum(values[-4:]) / 4
    avg_prev = sum(values[-8:-4]) / 4 or 1
    trend_pct = int(round((avg_last - avg_prev) / avg_prev * 100))

    peak_month = max(range(1, 13), key=lambda m: sum(
        p["value"] for p in interest if int(p["date"].split("-")[1]) == m
    ))
    seasonality = datetime.date(2000, peak_month, 1).strftime("%b")

    regions = [
        {"name": "France", "value": 92},
        {"name": "Belgium", "value": 74},
        {"name": "Switzerland", "value": 61},
        {"name": "Canada", "value": 48},
        {"name": "Germany", "value": 41},
        {"name": "United States", "value": 29},
    ]

    return {
        "interest": interest,
        "trend_pct": trend_pct,
        "seasonality": seasonality,
        "regions": regions,
        "top_market": regions[0]["name"],
        "opportunity": regions[1]["name"],
    }


def fetch_trends(keyword: str) -> dict[str, Any]:
    """
    Fetch Google Trends data for a keyword.

    Returns a dict with:
        interest:     list of {date, value} dicts (weekly, past 12 months)
        trend_pct:    integer percent change (last 4 weeks vs prior 4 weeks)
        seasonality:  month name of the historically highest-interest month
        regions:      list of {name, value} dicts (top 8 regions)
        top_market:   name of the #1 region
        opportunity:  simple qualitative label ('High' / 'Medium' / 'Low')
    """
    pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
    pytrends.build_payload(
        [keyword],
        timeframe="today 12-m",
        geo="",
        gprop="",
    )

    # --- Interest over time ---
    iot = pytrends.interest_over_time()
    if iot is None or iot.empty:
        raise ValueError(f"No interest-over-time data for keyword '{keyword}'")

    series = iot[keyword]

    interest: list[dict[str, Any]] = [
        {"date": str(ts.date()), "value": int(v)}
        for ts, v in series.items()
    ]

    # --- Trend percentage (last 4 weeks vs prior 4 weeks) ---
    values = series.tolist()
    last4 = values[-4:] if len(values) >= 4 else values
    prev4 = values[-8:-4] if len(values) >= 8 else values[:max(1, len(values) - 4)]
    avg_last = sum(last4) / len(last4) if last4 else 0
    avg_prev = sum(prev4) / len(prev4) if prev4 else 1
    trend_pct = int(round((avg_last - avg_prev) / max(avg_prev, 1) * 100))

    # --- Seasonality (peak month name across the year) ---
    monthly: dict[int, list[int]] = {}
    for ts, v in series.items():
        m = ts.month
        monthly.setdefault(m, []).append(int(v))
    avg_by_month = {m: sum(vs) / len(vs) for m, vs in monthly.items()}
    peak_month = max(avg_by_month, key=lambda m: avg_by_month[m], default=1)
    seasonality = datetime.date(2000, peak_month, 1).strftime("%b")

    # --- Interest by region ---
    ibr = pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=False, inc_geo_code=False)
    if ibr is None or ibr.empty:
        regions: list[dict[str, Any]] = []
    else:
        top = ibr[keyword].sort_values(ascending=False).head(8)
        regions = [{"name": str(name), "value": int(val)} for name, val in top.items() if val > 0]

    top_market = regions[0]["name"] if regions else "N/A"

    # --- Opportunity label ---
    max_val = regions[0]["value"] if regions else 0
    if max_val >= 75:
        opportunity = "High"
    elif max_val >= 40:
        opportunity = "Medium"
    else:
        opportunity = "Low"

    return {
        "interest": interest,
        "trend_pct": trend_pct,
        "seasonality": seasonality,
        "regions": regions,
        "top_market": top_market,
        "opportunity": opportunity,
    }
