"""Unit tests for logic/analysis.py — generate_search_queries, generate_market_analysis."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock, patch

from src.logic.analysis import generate_search_queries, generate_market_analysis, _coerce_to_str_list, _coerce_to_dict, _normalize_market_analysis_dict
from src.models.report import MarketAnalysis


# ── _coerce_to_str_list (unit) ────────────────────────────────────────────

def test_coerce_str_list_passthrough_real_list():
    assert _coerce_to_str_list(["a", "b"]) == ["a", "b"]

def test_coerce_str_list_json_string():
    assert _coerce_to_str_list('["desk mat", "office mat"]') == ["desk mat", "office mat"]

def test_coerce_str_list_python_repr_string():
    # What OpenHosta actually returns: str(list)
    assert _coerce_to_str_list("['desk mat', 'office mat']") == ["desk mat", "office mat"]

def test_coerce_str_list_single_string_fallback():
    result = _coerce_to_str_list("just a keyword")
    assert result == ["just a keyword"]

def test_coerce_str_list_empty_list():
    assert _coerce_to_str_list([]) == []

def test_coerce_str_list_none_returns_empty():
    assert _coerce_to_str_list(None) == []


# ── _coerce_to_dict (unit) ────────────────────────────────────────────────

def test_coerce_to_dict_passthrough_real_dict():
    d = {"viability_score": 74}
    assert _coerce_to_dict(d) == d

def test_coerce_to_dict_json_string():
    s = json.dumps({"viability_score": 74, "go_no_go": "conditional"})
    result = _coerce_to_dict(s)
    assert result["viability_score"] == 74

def test_coerce_to_dict_python_repr_string():
    s = "{'viability_score': 74, 'go_no_go': 'conditional'}"
    result = _coerce_to_dict(s)
    assert result["viability_score"] == 74

def test_coerce_to_dict_invalid_string_returns_empty():
    assert _coerce_to_dict("not a dict at all!!!") == {}

def test_coerce_to_dict_none_returns_empty():
    assert _coerce_to_dict(None) == {}


# ── _normalize_market_analysis_dict (unit) ───────────────────────────────

def test_normalize_viability_score_float_to_int():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "viability_score": 8.5})
    assert result["viability_score"] == 8  # Python banker's rounding: round(8.5) == 8
    assert isinstance(result["viability_score"], int)

def test_normalize_viability_score_int_unchanged():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "viability_score": 74})
    assert result["viability_score"] == 74

def test_normalize_go_no_go_capitalised():
    result = _normalize_market_analysis_dict({"go_no_go": "Go"})
    assert result["go_no_go"] == "go"

def test_normalize_go_no_go_no_go_variants():
    assert _normalize_market_analysis_dict({"go_no_go": "No-Go"})["go_no_go"] == "no-go"
    assert _normalize_market_analysis_dict({"go_no_go": "No Go"})["go_no_go"] == "no-go"
    assert _normalize_market_analysis_dict({"go_no_go": "Conditional"})["go_no_go"] == "conditional"

def test_normalize_criteria_list_of_strings():
    d = {"go_no_go": "go", "criteria": ["Customer demand", "Pricing"]}
    result = _normalize_market_analysis_dict(d)
    assert result["criteria"] == [
        {"label": "Customer demand", "score": 50},
        {"label": "Pricing", "score": 50},
    ]

def test_normalize_criteria_already_dicts_unchanged():
    criteria = [{"label": "Market size", "score": 80}]
    result = _normalize_market_analysis_dict({"go_no_go": "go", "criteria": criteria})
    assert result["criteria"] == criteria

def test_normalize_target_persona_string_to_dict():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "target_persona": "Remote workers"})
    assert result["target_persona"] == {"description": "Remote workers"}

def test_normalize_target_persona_dict_unchanged():
    tp = {"description": "Remote workers"}
    result = _normalize_market_analysis_dict({"go_no_go": "go", "target_persona": tp})
    assert result["target_persona"] == tp

def test_normalize_differentiation_angles_string_to_dict():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "differentiation_angles": "Eco packaging"})
    assert result["differentiation_angles"] == {"content": "Eco packaging"}

def test_normalize_differentiation_angles_list_to_dict():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "differentiation_angles": ["Eco", "Bundle"]})
    assert result["differentiation_angles"] == {"content": "Eco, Bundle"}

def test_normalize_competitive_overview_string_to_dict():
    result = _normalize_market_analysis_dict({"go_no_go": "go", "competitive_overview": "Moderate competition"})
    assert result["competitive_overview"] == {"content": "Moderate competition"}

def test_normalize_competitive_overview_list_of_products_to_dict():
    co = [{"title": "Product A", "price": "9.99"}, {"title": "Product B", "price": "14.99"}]
    result = _normalize_market_analysis_dict({"go_no_go": "go", "competitive_overview": co})
    assert result["competitive_overview"]["content"] == "Product A, Product B"


# ── generate_search_queries ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_search_queries_returns_list():
    keywords = ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=keywords)):
        result = await generate_search_queries("I want to sell desk mats")
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_generate_search_queries_returns_3_to_5_items():
    keywords = ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=keywords)):
        result = await generate_search_queries("desk mats for home office")
    assert 3 <= len(result) <= 5


@pytest.mark.asyncio
async def test_generate_search_queries_items_are_non_empty_strings():
    keywords = ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=keywords)):
        result = await generate_search_queries("desk mats")
    for kw in result:
        assert isinstance(kw, str)
        assert len(kw.strip()) > 0


@pytest.mark.asyncio
async def test_generate_search_queries_exactly_three_when_llm_returns_three():
    keywords = ["desk mat", "office mat", "wrist rest"]
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=keywords)):
        result = await generate_search_queries("ergonomic products")
    assert len(result) == 3


# ── generate_market_analysis ──────────────────────────────────────────────


SAMPLE_ANALYSIS_DICT = {
    "viability_score": 74,
    "go_no_go": "conditional",
    "summary": "Solid niche with moderate competition.",
    "analysis": "Demand is consistent year-round with a modest Q4 spike.",
    "key_risks": ["High competition", "Price pressure", "Seasonality"],
    "key_opportunities": ["Eco-friendly angle", "Bundle offers", "B2B market"],
    "criteria": [
        {"label": "Market size", "score": 80},
        {"label": "Competition", "score": 55},
        {"label": "Differentiation potential", "score": 70},
    ],
    "target_persona": {"description": "Remote workers aged 28-45"},
    "differentiation_angles": {"content": "Bundle with cable management tray"},
    "competitive_overview": {"content": "Top competitors include Logitech Desk Mat"},
}


@pytest.mark.asyncio
async def test_generate_market_analysis_returns_market_analysis_instance():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert isinstance(result, MarketAnalysis)


@pytest.mark.asyncio
async def test_generate_market_analysis_viability_score_is_0_to_100():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert 0 <= result.viability_score <= 100


@pytest.mark.asyncio
async def test_generate_market_analysis_go_no_go_is_valid():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert result.go_no_go in {"go", "no-go", "conditional"}


@pytest.mark.asyncio
async def test_generate_market_analysis_criteria_count_is_3_to_5():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert 3 <= len(result.criteria) <= 5


@pytest.mark.asyncio
async def test_generate_market_analysis_each_criterion_has_label_and_score():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    for criterion in result.criteria:
        assert isinstance(criterion.label, str)
        assert len(criterion.label) > 0
        assert 0 <= criterion.score <= 100


@pytest.mark.asyncio
async def test_generate_market_analysis_key_risks_has_three_items():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert len(result.key_risks) == 3


@pytest.mark.asyncio
async def test_generate_market_analysis_key_opportunities_has_three_items():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert len(result.key_opportunities) == 3


@pytest.mark.asyncio
async def test_generate_market_analysis_target_persona_description_is_non_empty():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert isinstance(result.target_persona.description, str)
    assert len(result.target_persona.description.strip()) > 0


@pytest.mark.asyncio
async def test_generate_market_analysis_differentiation_angles_content_is_non_empty():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert isinstance(result.differentiation_angles.content, str)
    assert len(result.differentiation_angles.content.strip()) > 0


@pytest.mark.asyncio
async def test_generate_market_analysis_competitive_overview_content_is_non_empty():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert isinstance(result.competitive_overview.content, str)
    assert len(result.competitive_overview.content.strip()) > 0


@pytest.mark.asyncio
async def test_generate_market_analysis_summary_is_non_empty():
    with patch("src.logic.analysis.emulate_async", AsyncMock(return_value=SAMPLE_ANALYSIS_DICT)):
        result = await generate_market_analysis("desk mats", [], {})
    assert isinstance(result.summary, str)
    assert len(result.summary.strip()) > 0
