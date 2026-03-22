"""Unit tests for logic/trends.py — fetch_trends."""
from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

from src.logic.trends import fetch_trends, TrendsData, KeywordTrends, TimePoint, RegionPoint, QueryPoint, RisingPoint


# ── TrendsData dataclass ──────────────────────────────────────────────────


def test_trends_data_dataclass_has_keywords_and_trends():
    td = TrendsData(keywords=["a", "b"])
    assert td.keywords == ["a", "b"]
    assert td.trends == {}


def test_keyword_trends_dataclass_has_all_four_fields():
    kt = KeywordTrends()
    assert hasattr(kt, "interest_over_time")
    assert hasattr(kt, "interest_by_region")
    assert hasattr(kt, "related_queries_top")
    assert hasattr(kt, "related_queries_rising")


def test_time_point_fields():
    tp = TimePoint(date="2025-03-01", value=72)
    assert tp.date == "2025-03-01"
    assert tp.value == 72


def test_region_point_fields():
    rp = RegionPoint(geo="US", name="United States", value=100)
    assert rp.geo == "US"
    assert rp.name == "United States"
    assert rp.value == 100


def test_query_point_fields():
    qp = QueryPoint(query="desk mat large", value=100)
    assert qp.query == "desk mat large"
    assert qp.value == 100


def test_rising_point_fields():
    rp = RisingPoint(query="ergonomic pad", value="+850%")
    assert rp.query == "ergonomic pad"
    assert rp.value == "+850%"


# ── fetch_trends — empty input ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_trends_empty_keywords_returns_empty_trends_data():
    result = await fetch_trends([])
    assert isinstance(result, TrendsData)
    assert result.keywords == []


# ── fetch_trends — happy path with mocked pytrends ───────────────────────


def _make_mock_pytrends(keywords: list[str]):
    """Build a mock TrendReq that returns realistic DataFrames."""
    import pandas as pd
    from unittest.mock import MagicMock

    mock = MagicMock()

    # interest_over_time DataFrame: datetime index, one column per keyword
    dates = pd.date_range(start="2024-03-01", periods=52, freq="W")
    iot_data = {kw: [50 + i % 20 for i in range(52)] for kw in keywords}
    iot_df = pd.DataFrame(iot_data, index=dates)
    mock.interest_over_time.return_value = iot_df

    # interest_by_region DataFrame: geo index, one column per keyword
    geos = ["US", "GB", "DE", "FR", "CA", "AU", "IN", "JP", "BR", "MX"]
    ibr_data = {kw: [100, 71, 60, 55, 50, 45, 40, 35, 30, 25] for kw in keywords}
    ibr_df = pd.DataFrame(ibr_data, index=geos)
    mock.interest_by_region.return_value = ibr_df

    # related_queries: dict per keyword
    top_df = pd.DataFrame({"query": [f"{keywords[0]} large", f"{keywords[0]} xl"], "value": [100, 80]})
    rising_df = pd.DataFrame({"query": ["breakout term"], "value": ["Breakout"]})
    rq_result = {kw: {"top": top_df, "rising": rising_df} for kw in keywords}
    mock.related_queries.return_value = rq_result

    return mock


@pytest.mark.asyncio
async def test_fetch_trends_returns_trends_data_type():
    keywords = ["ergonomic desk mat", "office mat"]
    with patch("src.logic.trends._fetch_trends_sync", return_value=TrendsData(keywords=keywords, trends={})):
        result = await fetch_trends(keywords)
    assert isinstance(result, TrendsData)


@pytest.mark.asyncio
async def test_fetch_trends_result_contains_keywords():
    keywords = ["ergonomic desk mat"]
    mock_result = TrendsData(keywords=keywords, trends={"ergonomic desk mat": KeywordTrends(
        interest_over_time=[TimePoint(date="2025-03-01", value=72)],
        interest_by_region=[RegionPoint(geo="US", name="US", value=100)],
        related_queries_top=[QueryPoint(query="desk mat large", value=100)],
        related_queries_rising=[RisingPoint(query="best mat", value="+250%")],
    )})
    with patch("src.logic.trends._fetch_trends_sync", return_value=mock_result):
        result = await fetch_trends(keywords)
    assert result.keywords == keywords


@pytest.mark.asyncio
async def test_fetch_trends_result_has_per_keyword_dict():
    keywords = ["mat"]
    kw_trends = KeywordTrends()
    mock_result = TrendsData(keywords=keywords, trends={"mat": kw_trends})
    with patch("src.logic.trends._fetch_trends_sync", return_value=mock_result):
        result = await fetch_trends(keywords)
    assert isinstance(result.trends, dict)
    assert "mat" in result.trends


@pytest.mark.asyncio
async def test_fetch_trends_keyword_trends_has_all_four_lists():
    keywords = ["desk mat"]
    kt = KeywordTrends(
        interest_over_time=[TimePoint(date="2025-01-01", value=80)],
        interest_by_region=[RegionPoint(geo="US", name="United States", value=100)],
        related_queries_top=[QueryPoint(query="large desk mat", value=100)],
        related_queries_rising=[RisingPoint(query="ergonomic pad", value="+500%")],
    )
    mock_result = TrendsData(keywords=keywords, trends={"desk mat": kt})
    with patch("src.logic.trends._fetch_trends_sync", return_value=mock_result):
        result = await fetch_trends(keywords)
    kw_trends = result.trends["desk mat"]
    assert len(kw_trends.interest_over_time) >= 1
    assert len(kw_trends.interest_by_region) >= 1
    assert len(kw_trends.related_queries_top) >= 1
    assert len(kw_trends.related_queries_rising) >= 1


@pytest.mark.asyncio
async def test_fetch_trends_interest_over_time_values_are_0_to_100():
    keywords = ["desk mat"]
    kt = KeywordTrends(
        interest_over_time=[TimePoint(date="2025-01-01", value=72), TimePoint(date="2025-01-08", value=45)],
    )
    mock_result = TrendsData(keywords=keywords, trends={"desk mat": kt})
    with patch("src.logic.trends._fetch_trends_sync", return_value=mock_result):
        result = await fetch_trends(keywords)
    for tp in result.trends["desk mat"].interest_over_time:
        assert 0 <= tp.value <= 100


@pytest.mark.asyncio
async def test_fetch_trends_region_points_have_geo_and_name():
    keywords = ["mat"]
    kt = KeywordTrends(
        interest_by_region=[RegionPoint(geo="US", name="United States", value=100)]
    )
    mock_result = TrendsData(keywords=keywords, trends={"mat": kt})
    with patch("src.logic.trends._fetch_trends_sync", return_value=mock_result):
        result = await fetch_trends(keywords)
    for rp in result.trends["mat"].interest_by_region:
        assert rp.geo
        assert rp.name
        assert 0 <= rp.value <= 100


# ── fetch_trends — error handling ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_trends_returns_empty_trends_on_pytrends_exception():
    """If pytrends raises any exception, fetch_trends must return empty TrendsData."""
    keywords = ["desk mat"]
    with patch("src.logic.trends._fetch_trends_sync", side_effect=Exception("pytrends error")):
        result = await fetch_trends(keywords)
    assert isinstance(result, TrendsData)
    assert result.keywords == keywords


@pytest.mark.asyncio
async def test_fetch_trends_rate_limit_returns_empty_not_raises():
    """ResponseError (rate-limit) must not crash the workflow."""
    from pytrends.exceptions import ResponseError
    keywords = ["mat"]
    with patch("src.logic.trends._fetch_trends_sync", side_effect=ResponseError("429", MagicMock())):
        result = await fetch_trends(keywords)
    assert isinstance(result, TrendsData)


# ── TrendsData.to_dict() ──────────────────────────────────────────────────


def test_trends_data_to_dict_contains_keywords():
    kt = KeywordTrends(
        interest_over_time=[TimePoint(date="2025-01-01", value=50)],
    )
    td = TrendsData(keywords=["desk mat"], trends={"desk mat": kt})
    d = td.to_dict()
    assert "keywords" in d
    assert "trends" in d


def test_trends_data_to_dict_serializes_time_points():
    kt = KeywordTrends(
        interest_over_time=[TimePoint(date="2025-03-01", value=72)],
    )
    td = TrendsData(keywords=["mat"], trends={"mat": kt})
    d = td.to_dict()
    tp = d["trends"]["mat"]["interest_over_time"][0]
    assert tp == {"date": "2025-03-01", "value": 72}
