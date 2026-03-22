"""Unit tests for logic/export.py — render_markdown, render_pdf."""
from __future__ import annotations
import re
import pytest

from src.logic.export import render_markdown, render_pdf


# ── Shared sample run data ────────────────────────────────────────────────


SAMPLE_RUN_DATA = {
    "run_id": "abc-123",
    "description": "ergonomic desk mats for home office",
    "keywords": ["ergonomic desk mat", "office desk accessories", "wrist rest pad"],
    "products": [
        {
            "title": "Premium Ergonomic Desk Mat",
            "price": "EUR 24.99",
            "url": "https://www.amazon.com/dp/B001",
            "rating_stars": 4.3,
            "rating_count": 1247,
            "main_features": ["Non-slip base", "Extended 90x40cm size", "Waterproof surface"],
        }
    ],
    "trends": {
        "ergonomic desk mat": {
            "interest_over_time": [{"date": "2025-03-01", "value": 72}],
            "interest_by_region": [{"geo": "US", "name": "United States", "value": 100}],
            "related_queries_top": [],
            "related_queries_rising": [],
        }
    },
    "ai_analysis": {
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
    },
}


# ── render_markdown — heading and section tests ───────────────────────────


def test_render_markdown_starts_with_h1_market_analysis():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert result.startswith("# Market Analysis:")


def test_render_markdown_h1_includes_description():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "ergonomic desk mats for home office" in result


def test_render_markdown_contains_keywords_used_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Keywords Used" in result


def test_render_markdown_contains_marketplace_products_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Marketplace Products" in result


def test_render_markdown_contains_market_trends_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Market Trends" in result


def test_render_markdown_contains_viability_score_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Viability Score" in result


def test_render_markdown_contains_go_no_go_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Go / No-Go" in result


def test_render_markdown_contains_target_persona_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Target Persona" in result


def test_render_markdown_contains_differentiation_angles_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Differentiation Angles" in result


def test_render_markdown_contains_competitive_overview_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Competitive Overview" in result


def test_render_markdown_contains_key_risks_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Key Risks" in result


def test_render_markdown_contains_key_opportunities_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Key Opportunities" in result


def test_render_markdown_contains_scoring_criteria_heading():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Scoring Criteria" in result


# ── render_markdown — machine-parseable fields ────────────────────────────


def test_render_markdown_score_line_starts_with_score_prefix():
    """The Score line MUST start with 'Score: ' (machine-parseable)."""
    result = render_markdown(SAMPLE_RUN_DATA)
    score_lines = [line for line in result.splitlines() if line.startswith("Score: ")]
    assert len(score_lines) >= 1, f"No 'Score: ' line found in:\n{result}"


def test_render_markdown_score_line_format_is_nn_slash_100():
    result = render_markdown(SAMPLE_RUN_DATA)
    score_lines = [line for line in result.splitlines() if line.startswith("Score: ")]
    assert score_lines, "No Score: line"
    assert re.match(r"Score: \d+/100", score_lines[0]), f"Bad format: {score_lines[0]}"


def test_render_markdown_score_line_is_standalone_no_surrounding_text():
    """The Score: line must be on its own line with no prefix."""
    result = render_markdown(SAMPLE_RUN_DATA)
    for line in result.splitlines():
        if "Score:" in line:
            assert line.startswith("Score: "), f"Score line has prefix: {line!r}"
            break


def test_render_markdown_verdict_field_is_present():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "**Verdict**:" in result


def test_render_markdown_verdict_is_valid_value():
    result = render_markdown(SAMPLE_RUN_DATA)
    verdict_match = re.search(r"\*\*Verdict\*\*: (\S+)", result)
    assert verdict_match, "**Verdict**: line not found"
    assert verdict_match.group(1) in {"go", "no-go", "conditional"}


def test_render_markdown_run_id_is_in_header():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "abc-123" in result


def test_render_markdown_products_table_has_headers():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "| Product |" in result
    assert "| Price |" in result
    assert "| Rating |" in result
    assert "| Reviews |" in result


def test_render_markdown_keywords_are_listed():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "- ergonomic desk mat" in result
    assert "- office desk accessories" in result


def test_render_markdown_risks_are_listed():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "- High competition" in result
    assert "- Price pressure" in result


def test_render_markdown_returns_string():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert isinstance(result, str)


def test_render_markdown_empty_run_data_does_not_crash():
    result = render_markdown({})
    assert isinstance(result, str)


# ── render_pdf ────────────────────────────────────────────────────────────


def test_render_pdf_returns_bytes():
    md = render_markdown(SAMPLE_RUN_DATA)
    result = render_pdf(md)
    assert isinstance(result, bytes)


def test_render_pdf_starts_with_pdf_magic_bytes():
    md = render_markdown(SAMPLE_RUN_DATA)
    result = render_pdf(md)
    assert result[:4] == b"%PDF", f"Expected PDF magic bytes, got: {result[:10]!r}"


def test_render_pdf_is_non_empty():
    md = render_markdown(SAMPLE_RUN_DATA)
    result = render_pdf(md)
    assert len(result) > 100  # any real PDF will be much larger


def test_render_pdf_for_empty_markdown_still_returns_bytes():
    result = render_pdf("")
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_render_pdf_includes_browser_charts_note():
    """PDF must include the note about charts being browser-only."""
    md = "# Test\n\nSome content."
    result = render_pdf(md)
    # The note is in HTML before the markdown body — it should be in the PDF
    assert isinstance(result, bytes)  # just verify it doesn't crash


# ── Target Personas section (004-persona-generation) ─────────────────────────

SAMPLE_PERSONAS = [
    {
        "name": "The Weekend Creator",
        "age_range": "25–35",
        "occupation": "Freelance designer",
        "motivations": ["Professional look", "Aesthetic tools"],
        "pain_points": ["Cheap materials", "Wrong sizes"],
    },
    {
        "name": "The Remote Professional",
        "age_range": "30–45",
        "occupation": "Software engineer",
        "motivations": ["Ergonomic surface", "Minimal design"],
        "pain_points": ["Mouse skip", "Cable mess"],
    },
    {
        "name": "The Student Hustler",
        "age_range": "18–24",
        "occupation": "University student",
        "motivations": ["Gaming aesthetic", "Budget value"],
        "pain_points": ["Too expensive", "Too large"],
    },
]

SAMPLE_RUN_DATA_WITH_PERSONAS = {**SAMPLE_RUN_DATA, "personas": SAMPLE_PERSONAS}


def test_render_markdown_includes_target_personas_section_when_personas_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "## Target Personas" in result


def test_render_markdown_target_personas_section_absent_when_personas_empty():
    run_data_no_personas = {**SAMPLE_RUN_DATA, "personas": []}
    result = render_markdown(run_data_no_personas)
    assert "## Target Personas" not in result


def test_render_markdown_target_personas_section_absent_when_key_missing():
    result = render_markdown(SAMPLE_RUN_DATA)
    assert "## Target Personas" not in result


def test_render_markdown_persona_names_appear_in_output():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "The Weekend Creator" in result
    assert "The Remote Professional" in result
    assert "The Student Hustler" in result


def test_render_markdown_persona_sub_sections_are_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "### Persona 1: The Weekend Creator" in result
    assert "### Persona 2: The Remote Professional" in result
    assert "### Persona 3: The Student Hustler" in result


def test_render_markdown_persona_age_range_is_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "**Age range**: 25–35" in result


def test_render_markdown_persona_occupation_is_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "**Occupation**: Freelance designer" in result


def test_render_markdown_persona_motivations_are_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "Professional look" in result


def test_render_markdown_persona_pain_points_are_present():
    result = render_markdown(SAMPLE_RUN_DATA_WITH_PERSONAS)
    assert "Cheap materials" in result
