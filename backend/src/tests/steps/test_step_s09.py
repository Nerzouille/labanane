"""Unit tests for Step 9 — ReportGenerationStep."""
import pytest
from unittest.mock import patch

from src.workflow.steps.s09_report import ReportGenerationStep
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_CONFIRMED = {
    "keyword_confirmation": {"keywords": ["desk mat", "office mat", "wrist rest"]},
    "product_research": {
        "products": [
            {"title": "Desk Mat", "price": "EUR 24.99", "url": "https://amazon.com/dp/B001",
             "rating_stars": 4.3, "rating_count": 1247,
             "main_features": ["Non-slip", "Large", "Waterproof"]},
        ],
        "source_keywords": ["desk mat"],
    },
    "market_research": {
        "keywords": ["desk mat"],
        "sources_available": ["google_trends"],
        "sources_unavailable": [],
        "trends": {"desk mat": {"interest_over_time": [{"date": "2025-01-01", "value": 72}],
                                "interest_by_region": [], "related_queries_top": [], "related_queries_rising": []}},
    },
    "ai_analysis": {
        "viability_score": 74,
        "go_no_go": "conditional",
        "summary": "Solid niche.",
        "analysis": "Consistent demand.",
        "key_risks": ["Competition", "Price", "Season"],
        "key_opportunities": ["Eco", "Bundle", "B2B"],
        "criteria": [{"label": "Size", "score": 80}],
        "target_persona": {"description": "Remote workers"},
        "differentiation_angles": {"content": "Bundle"},
        "competitive_overview": {"content": "Logitech"},
    },
}


@pytest.fixture
def step():
    return ReportGenerationStep()


@pytest.fixture
def full_run():
    return make_run(confirmed_outputs=SAMPLE_CONFIRMED)


def test_step_id_is_report_generation(step):
    assert step.step_id == "report_generation"


def test_step_type_is_derivation(step):
    assert step.step_type == "derivation"


def test_component_type_is_report(step):
    assert step.component_type == "report"


@pytest.mark.asyncio
async def test_execute_yields_step_result(step, full_run):
    messages = await collect_step_messages(step, full_run)
    types = [m["type"] for m in messages]
    assert "step_result" in types


@pytest.mark.asyncio
async def test_execute_step_result_has_markdown_available_true(step, full_run):
    messages = await collect_step_messages(step, full_run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert sr["data"]["markdown_available"] is True


@pytest.mark.asyncio
async def test_execute_step_result_has_run_id(step, full_run):
    messages = await collect_step_messages(step, full_run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "run_id" in sr["data"]
    assert sr["data"]["run_id"] == full_run.run_id


@pytest.mark.asyncio
async def test_execute_stores_markdown_in_reports_store(step, full_run):
    import src.store as store_mod
    # Clear store before test
    store_mod._reports.clear()
    messages = await collect_step_messages(step, full_run)
    assert full_run.run_id in store_mod._reports
    assert isinstance(store_mod._reports[full_run.run_id], str)
    assert len(store_mod._reports[full_run.run_id]) > 0


@pytest.mark.asyncio
async def test_execute_stored_markdown_starts_with_heading(step, full_run):
    import src.store as store_mod
    store_mod._reports.clear()
    await collect_step_messages(step, full_run)
    md = store_mod._reports.get(full_run.run_id, "")
    assert md.startswith("# Market Analysis:")


@pytest.mark.asyncio
async def test_execute_component_type_in_result(step, full_run):
    messages = await collect_step_messages(step, full_run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert sr["component_type"] == "report"


@pytest.mark.asyncio
async def test_execute_no_step_processing_for_derivation(step, full_run):
    messages = await collect_step_messages(step, full_run)
    assert all(m["type"] != "step_processing" for m in messages)
