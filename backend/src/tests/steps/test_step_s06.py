"""Unit tests for Step 6 — MarketResearchStep."""
import pytest
from unittest.mock import patch

from src.workflow.steps.s06_market_research import MarketResearchStep
from src.logic.trends import TrendsData, KeywordTrends, TimePoint, RegionPoint, QueryPoint, RisingPoint
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_KEYWORDS = ["ergonomic desk mat", "office mat"]


def _make_trends_data(keywords=SAMPLE_KEYWORDS, has_trends=True) -> TrendsData:
    if not has_trends:
        return TrendsData(keywords=keywords, trends={})
    kt = KeywordTrends(
        interest_over_time=[TimePoint(date="2025-03-01", value=72)],
        interest_by_region=[RegionPoint(geo="US", name="United States", value=100)],
        related_queries_top=[QueryPoint(query="desk mat large", value=100)],
        related_queries_rising=[RisingPoint(query="best ergonomic mat", value="+250%")],
    )
    return TrendsData(keywords=keywords, trends={kw: kt for kw in keywords})


@pytest.fixture
def step():
    return MarketResearchStep()


def test_step_id_is_market_research(step):
    assert step.step_id == "market_research"


def test_step_type_is_system_processing(step):
    assert step.step_type == "system_processing"


def test_component_type_is_market_data(step):
    assert step.component_type == "market_data"


@pytest.mark.asyncio
async def test_execute_yields_step_processing_first(step):
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               return_value=_make_trends_data()):
        messages = await collect_step_messages(step, run)
    # Can't await because fetch_trends is patched as sync value; use AsyncMock
    assert messages[0]["type"] == "step_processing"


@pytest.mark.asyncio
async def test_execute_yields_step_processing_before_step_result(step):
    from unittest.mock import AsyncMock
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               AsyncMock(return_value=_make_trends_data())):
        messages = await collect_step_messages(step, run)
    types = [m["type"] for m in messages]
    assert types.index("step_processing") < types.index("step_result")


@pytest.mark.asyncio
async def test_execute_step_result_contains_market_data_result_shape(step):
    from unittest.mock import AsyncMock
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               AsyncMock(return_value=_make_trends_data())):
        messages = await collect_step_messages(step, run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "keywords" in sr["data"]
    assert "sources_available" in sr["data"]
    assert "sources_unavailable" in sr["data"]
    assert "trends" in sr["data"]


@pytest.mark.asyncio
async def test_execute_reads_keywords_via_run_get_output(step):
    from unittest.mock import AsyncMock
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    keywords_read = []
    original = run.get_output
    def tracked(step_id):
        r = original(step_id)
        if step_id == "keyword_refinement":
            keywords_read.append(r)
        return r
    run.get_output = tracked
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               AsyncMock(return_value=_make_trends_data())):
        await collect_step_messages(step, run)
    assert len(keywords_read) > 0


@pytest.mark.asyncio
async def test_execute_sources_available_when_trends_present(step):
    from unittest.mock import AsyncMock
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               AsyncMock(return_value=_make_trends_data(has_trends=True))):
        messages = await collect_step_messages(step, run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "google_trends" in sr["data"]["sources_available"]
    assert sr["data"]["sources_unavailable"] == []


@pytest.mark.asyncio
async def test_execute_sources_unavailable_when_trends_empty(step):
    from unittest.mock import AsyncMock
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s06_market_research.fetch_trends",
               AsyncMock(return_value=_make_trends_data(has_trends=False))):
        messages = await collect_step_messages(step, run)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "google_trends" in sr["data"]["sources_unavailable"]
    assert sr["data"]["sources_available"] == []
