"""Business logic — Google Trends data fetching via pytrends.

Pure async functions. No workflow state, no WebSocket access.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, asdict


@dataclass
class TimePoint:
    date: str    # ISO date string "YYYY-MM-DD"
    value: int   # 0–100 relative interest


@dataclass
class RegionPoint:
    geo: str     # ISO 3166-1 alpha-2 country code
    name: str    # human-readable country name
    value: int   # 0–100 relative interest


@dataclass
class QueryPoint:
    query: str
    value: int   # absolute relative value (top queries)


@dataclass
class RisingPoint:
    query: str
    value: str   # e.g. "+850%", "Breakout"


@dataclass
class KeywordTrends:
    interest_over_time: list[TimePoint] = field(default_factory=list)    # 52 weekly points
    interest_by_region: list[RegionPoint] = field(default_factory=list)  # top 10 countries
    related_queries_top: list[QueryPoint] = field(default_factory=list)  # top 10
    related_queries_rising: list[RisingPoint] = field(default_factory=list)  # top 5


@dataclass
class TrendsData:
    keywords: list[str]
    trends: dict[str, KeywordTrends] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a plain dict suitable for JSON transmission."""
        return {
            "keywords": self.keywords,
            "trends": {
                kw: {
                    "interest_over_time": [asdict(p) for p in kt.interest_over_time],
                    "interest_by_region": [asdict(p) for p in kt.interest_by_region],
                    "related_queries_top": [asdict(p) for p in kt.related_queries_top],
                    "related_queries_rising": [asdict(p) for p in kt.related_queries_rising],
                }
                for kw, kt in self.trends.items()
            },
        }


async def fetch_trends(keywords: list[str]) -> TrendsData:
    """Fetch Google Trends data for the given keywords.

    Returns TrendsData with:
    - interest_over_time: 52 weekly data points (past 12 months), values 0-100
    - interest_by_region: top 10 countries, values 0-100 relative
    - related_queries_top: top 10 stable queries
    - related_queries_rising: top 5 breakout queries

    Handles pytrends rate-limiting with exponential backoff (max 3 attempts).
    If Google Trends is unavailable, returns empty TrendsData with the keywords list intact.
    """
    if not keywords:
        return TrendsData(keywords=[])

    try:
        return await asyncio.get_event_loop().run_in_executor(
            None, _fetch_trends_sync, keywords
        )
    except Exception:
        # Return empty trends rather than crashing the workflow
        return TrendsData(keywords=keywords)


def _fetch_trends_sync(keywords: list[str]) -> TrendsData:
    """Synchronous pytrends call, run in a thread executor."""
    import time
    from pytrends.request import TrendReq

    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    trends: dict[str, KeywordTrends] = {}

    for attempt in range(3):
        try:
            pytrends.build_payload(keywords, timeframe="today 12-m", geo="")
            break
        except Exception:
            if attempt == 2:
                return TrendsData(keywords=keywords)
            time.sleep(2 ** attempt + 1)

    # Interest over time
    try:
        iot_df = pytrends.interest_over_time()
        for kw in keywords:
            trends.setdefault(kw, KeywordTrends())
            if kw in iot_df.columns:
                for ts, row in iot_df.iterrows():
                    trends[kw].interest_over_time.append(
                        TimePoint(date=str(ts.date()), value=int(row[kw]))
                    )
    except Exception:
        pass

    # Interest by region
    try:
        ibr_df = pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=True)
        ibr_df = ibr_df.sum(axis=1).nlargest(10)
        for geo, val in ibr_df.items():
            for kw in keywords:
                trends.setdefault(kw, KeywordTrends())
            # Region data is shared across keywords; attach to all
            for kw in keywords:
                trends[kw].interest_by_region.append(
                    RegionPoint(geo=str(geo), name=str(geo), value=int(val))
                )
            # Only build list once then break — per-keyword region data needs separate calls
            break
        # Proper per-keyword region data
        for kw in keywords:
            trends[kw].interest_by_region = []
        for kw in keywords:
            try:
                pytrends.build_payload([kw], timeframe="today 12-m", geo="")
                ibr_df = pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=True)
                if kw in ibr_df.columns:
                    top10 = ibr_df[kw].nlargest(10)
                    for geo, val in top10.items():
                        trends[kw].interest_by_region.append(
                            RegionPoint(geo=str(geo), name=str(geo), value=int(val))
                        )
            except Exception:
                pass
        # Rebuild payload for all keywords for related queries
        pytrends.build_payload(keywords, timeframe="today 12-m", geo="")
    except Exception:
        pass

    # Related queries
    try:
        rq = pytrends.related_queries()
        for kw in keywords:
            trends.setdefault(kw, KeywordTrends())
            kw_data = rq.get(kw, {})
            top_df = kw_data.get("top")
            if top_df is not None and not top_df.empty:
                for _, row in top_df.head(10).iterrows():
                    trends[kw].related_queries_top.append(
                        QueryPoint(query=str(row["query"]), value=int(row["value"]))
                    )
            rising_df = kw_data.get("rising")
            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.head(5).iterrows():
                    trends[kw].related_queries_rising.append(
                        RisingPoint(query=str(row["query"]), value=str(row["value"]))
                    )
    except Exception:
        pass

    return TrendsData(keywords=keywords, trends=trends)
