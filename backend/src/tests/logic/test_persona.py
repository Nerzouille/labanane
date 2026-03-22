"""Unit tests for logic/persona.py — generate_personas and helpers."""
from __future__ import annotations
import json
import pytest
from unittest.mock import AsyncMock, patch

from src.logic.persona import (
    generate_personas,
    _coerce_to_list,
    _normalize_persona_list,
)
from src.models.report import PersonaSet


# ── _coerce_to_list ───────────────────────────────────────────────────────────

def test_coerce_to_list_passthrough_real_list():
    data = [{"name": "X"}, {"name": "Y"}]
    assert _coerce_to_list(data) is data


def test_coerce_to_list_json_string():
    s = json.dumps([{"name": "X"}, {"name": "Y"}])
    result = _coerce_to_list(s)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "X"


def test_coerce_to_list_python_repr_string():
    s = "[{'name': 'X'}, {'name': 'Y'}]"
    result = _coerce_to_list(s)
    assert isinstance(result, list)
    assert len(result) == 2


def test_coerce_to_list_invalid_string_returns_empty():
    assert _coerce_to_list("not a list at all!!!") == []


def test_coerce_to_list_none_returns_empty():
    assert _coerce_to_list(None) == []


def test_coerce_to_list_dict_returns_empty():
    # A dict is not a list — should return []
    assert _coerce_to_list({"name": "X"}) == []


# ── _normalize_persona_list ───────────────────────────────────────────────────

def _make_persona(**kwargs) -> dict:
    base = {
        "name": "Test",
        "age_range": "25–35",
        "occupation": "Designer",
        "motivations": ["m1", "m2"],
        "pain_points": ["p1", "p2"],
    }
    base.update(kwargs)
    return base


def test_normalize_persona_list_returns_exactly_3_when_5_given():
    raw = [_make_persona(name=f"P{i}") for i in range(5)]
    result = _normalize_persona_list(raw)
    assert len(result) == 3


def test_normalize_persona_list_pads_to_3_when_1_given():
    raw = [_make_persona(name="Solo")]
    result = _normalize_persona_list(raw)
    assert len(result) == 3


def test_normalize_persona_list_pads_to_3_when_empty():
    result = _normalize_persona_list([])
    assert len(result) == 3


def test_normalize_persona_list_fills_missing_name_with_unknown():
    raw = [{}]
    result = _normalize_persona_list(raw)
    assert result[0]["name"] == "Unknown"


def test_normalize_persona_list_fills_missing_lists_with_empty():
    raw = [{"name": "X"}]
    result = _normalize_persona_list(raw)
    assert result[0]["motivations"] == []
    assert result[0]["pain_points"] == []


def test_normalize_persona_list_preserves_valid_data():
    raw = [_make_persona(name="Creator")]
    result = _normalize_persona_list(raw)
    assert result[0]["name"] == "Creator"
    assert result[0]["motivations"] == ["m1", "m2"]


def test_normalize_persona_list_coerces_string_item_to_dict():
    raw = ["just a string description"]
    result = _normalize_persona_list(raw)
    # String becomes a persona with name set and lists empty
    assert result[0]["name"] == "just a string description"
    assert result[0]["motivations"] == []


def test_normalize_persona_list_ignores_non_list_motivations():
    raw = [{"name": "X", "motivations": "not a list"}]
    result = _normalize_persona_list(raw)
    assert result[0]["motivations"] == []


# ── generate_personas ─────────────────────────────────────────────────────────

SAMPLE_PRODUCTS = [
    {"title": "Desk Mat", "price": "EUR 20", "url": "https://amazon.com/dp/B001",
     "rating_stars": 4.2, "rating_count": 500, "main_features": ["a", "b", "c"]},
]
SAMPLE_AI = {
    "viability_score": 74,
    "go_no_go": "conditional",
    "summary": "Solid niche.",
    "key_risks": ["Competition"],
    "key_opportunities": ["Eco angle"],
}
SAMPLE_PERSONA_LIST = [
    {"name": "Creator", "age_range": "25–35", "occupation": "Designer",
     "motivations": ["Style", "Quality"], "pain_points": ["Price", "Durability"]},
    {"name": "Professional", "age_range": "30–45", "occupation": "Engineer",
     "motivations": ["Ergonomics", "Focus"], "pain_points": ["Cables", "Slipping"]},
    {"name": "Student", "age_range": "18–24", "occupation": "University student",
     "motivations": ["Budget", "Aesthetic"], "pain_points": ["Too expensive", "Too big"]},
]


@pytest.mark.asyncio
async def test_generate_personas_returns_persona_set():
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=SAMPLE_PERSONA_LIST)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    assert isinstance(result, PersonaSet)


@pytest.mark.asyncio
async def test_generate_personas_has_exactly_3_personas():
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=SAMPLE_PERSONA_LIST)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    assert len(result.personas) == 3


@pytest.mark.asyncio
async def test_generate_personas_each_persona_has_name():
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=SAMPLE_PERSONA_LIST)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    for persona in result.personas:
        assert isinstance(persona.name, str)
        assert len(persona.name.strip()) > 0


@pytest.mark.asyncio
async def test_generate_personas_each_persona_has_age_range():
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=SAMPLE_PERSONA_LIST)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    for persona in result.personas:
        assert isinstance(persona.age_range, str)


@pytest.mark.asyncio
async def test_generate_personas_handles_json_string_response():
    json_str = json.dumps(SAMPLE_PERSONA_LIST)
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=json_str)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    assert isinstance(result, PersonaSet)
    assert len(result.personas) == 3


@pytest.mark.asyncio
async def test_generate_personas_handles_empty_products_and_analysis():
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=SAMPLE_PERSONA_LIST)):
        result = await generate_personas("desk mats", [], {})
    assert isinstance(result, PersonaSet)
    assert len(result.personas) == 3


@pytest.mark.asyncio
async def test_generate_personas_pads_when_llm_returns_fewer():
    short_list = [SAMPLE_PERSONA_LIST[0]]  # only 1 persona
    with patch("src.logic.persona.emulate_async", AsyncMock(return_value=short_list)):
        result = await generate_personas("desk mats", SAMPLE_PRODUCTS, SAMPLE_AI)
    assert len(result.personas) == 3
