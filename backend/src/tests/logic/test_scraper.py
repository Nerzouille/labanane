"""Unit tests for logic/scraper.py — clean_html_for_llm and fetch_html."""
from __future__ import annotations
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from src.logic.scraper import clean_html_for_llm, fetch_html, parse_marketplace_data, _coerce_to_list_of_dicts


# ── _coerce_to_list_of_dicts (unit) ──────────────────────────────────────

def test_coerce_list_of_dicts_passthrough_real_list():
    data = [{"title": "A", "price": "9.99"}]
    assert _coerce_to_list_of_dicts(data) == data

def test_coerce_list_of_dicts_json_string():
    s = '[{"title": "A", "price": "9.99"}]'
    result = _coerce_to_list_of_dicts(s)
    assert len(result) == 1
    assert result[0]["title"] == "A"

def test_coerce_list_of_dicts_python_repr_string():
    s = "[{'title': 'A', 'price': '9.99'}]"
    result = _coerce_to_list_of_dicts(s)
    assert len(result) == 1
    assert result[0]["title"] == "A"

def test_coerce_list_of_dicts_filters_non_dicts():
    assert _coerce_to_list_of_dicts(["not", "dicts"]) == []

def test_coerce_list_of_dicts_invalid_string_returns_empty():
    assert _coerce_to_list_of_dicts("garbage") == []

def test_coerce_list_of_dicts_none_returns_empty():
    assert _coerce_to_list_of_dicts(None) == []


# ── clean_html_for_llm (pure function) ───────────────────────────────────


def test_clean_html_strips_script_tags():
    html = "<html><body><p>Hello</p><script>alert('xss')</script></body></html>"
    result = clean_html_for_llm(html)
    assert "<script>" not in result
    assert "alert" not in result


def test_clean_html_strips_style_tags():
    html = "<html><head><style>body{color:red}</style></head><body>Content</body></html>"
    result = clean_html_for_llm(html)
    assert "<style>" not in result
    assert "color:red" not in result


def test_clean_html_strips_svg_tags():
    html = "<html><body><svg><path d='M0,0'/></svg><p>Text</p></body></html>"
    result = clean_html_for_llm(html)
    assert "<svg>" not in result


def test_clean_html_injects_href_text():
    html = '<html><body><a href="https://example.com/product">Buy Now</a></body></html>'
    result = clean_html_for_llm(html)
    assert "https://example.com/product" in result


def test_clean_html_returns_non_empty_for_valid_html():
    html = "<html><body><p>Product: Ergonomic Chair</p></body></html>"
    result = clean_html_for_llm(html)
    assert isinstance(result, str)
    assert len(result) > 0


def test_clean_html_preserves_product_text():
    html = "<html><body><p>Title: Ergonomic Desk Mat</p><p>Price: $24.99</p></body></html>"
    result = clean_html_for_llm(html)
    assert "Ergonomic Desk Mat" in result
    assert "24.99" in result


def test_clean_html_handles_empty_input():
    result = clean_html_for_llm("")
    assert isinstance(result, str)


def test_clean_html_truncates_at_max_length():
    long_html = "<p>" + "x" * 40000 + "</p>"
    result = clean_html_for_llm(long_html)
    assert len(result) <= 30000


def test_clean_html_removes_noscript_tags():
    html = "<html><body><noscript>Enable JS</noscript><p>Real content</p></body></html>"
    result = clean_html_for_llm(html)
    assert "Enable JS" not in result


# ── fetch_html ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_html_returns_string_on_200():
    """fetch_html returns the response body on HTTP 200."""
    fake_html = "<html><body><p>Mock product page</p></body></html>"
    mock_response = MagicMock(status_code=200, text=fake_html)
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await fetch_html("Amazon", "desk mat")
    assert result == fake_html


@pytest.mark.asyncio
async def test_fetch_html_fallback_on_503():
    """fetch_html returns a fallback string after two 503 responses."""
    mock_response = MagicMock(status_code=503, text="")
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("asyncio.sleep", AsyncMock()):
        result = await fetch_html("Amazon", "test query")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_fetch_html_retries_once_on_429():
    """fetch_html retries exactly once on 429 before giving up."""
    mock_response = MagicMock(status_code=429, text="")
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("asyncio.sleep", AsyncMock()):
        result = await fetch_html("Amazon", "desk mat")
    assert mock_client.get.call_count == 2  # initial + one retry
    assert isinstance(result, str)


# ── parse_marketplace_data ────────────────────────────────────────────────


SAMPLE_PRODUCTS_DICTS = [
    {
        "title": "Ergonomic Desk Mat",
        "price": "EUR 24.99",
        "url": "https://www.amazon.com/dp/B001",
        "rating_stars": 4.3,
        "rating_count": 1247,
        "main_features": ["Non-slip", "Large size", "Waterproof"],
    },
    {
        "title": "Office Desk Pad",
        "price": "EUR 18.99",
        "url": "https://www.amazon.com/dp/B002",
        "rating_stars": 4.1,
        "rating_count": 893,
        "main_features": ["PU leather", "Double-sided", "Anti-slip"],
    },
]


@pytest.mark.asyncio
async def test_parse_marketplace_data_returns_list():
    with patch("src.logic.scraper.emulate_async", AsyncMock(return_value=SAMPLE_PRODUCTS_DICTS)):
        result = await parse_marketplace_data("cleaned html text")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_parse_marketplace_data_returns_products_with_required_fields():
    with patch("src.logic.scraper.emulate_async", AsyncMock(return_value=SAMPLE_PRODUCTS_DICTS)):
        result = await parse_marketplace_data("html")
    for p in result:
        assert "title" in p
        assert "price" in p
        assert "url" in p
        assert "rating_stars" in p
        assert "rating_count" in p
        assert "main_features" in p


@pytest.mark.asyncio
async def test_parse_marketplace_data_rating_stars_is_float():
    with patch("src.logic.scraper.emulate_async", AsyncMock(return_value=SAMPLE_PRODUCTS_DICTS)):
        result = await parse_marketplace_data("html")
    for p in result:
        assert isinstance(p["rating_stars"], (int, float))
        assert 0.0 <= p["rating_stars"] <= 5.0


@pytest.mark.asyncio
async def test_parse_marketplace_data_rating_count_is_int():
    with patch("src.logic.scraper.emulate_async", AsyncMock(return_value=SAMPLE_PRODUCTS_DICTS)):
        result = await parse_marketplace_data("html")
    for p in result:
        assert isinstance(p["rating_count"], int)
        assert p["rating_count"] >= 0


@pytest.mark.asyncio
async def test_parse_marketplace_data_main_features_has_three_strings():
    with patch("src.logic.scraper.emulate_async", AsyncMock(return_value=SAMPLE_PRODUCTS_DICTS)):
        result = await parse_marketplace_data("html")
    for p in result:
        assert len(p["main_features"]) == 3
        for feature in p["main_features"]:
            assert isinstance(feature, str)
