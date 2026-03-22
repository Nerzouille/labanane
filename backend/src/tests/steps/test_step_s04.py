"""Unit tests for Step 4 — ProductResearchStep."""
import pytest
from unittest.mock import AsyncMock, patch

from src.workflow.steps.s04_product_research import ProductResearchStep
from src.workflow.step_base import StepError
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_KEYWORDS = ["ergonomic desk mat", "office mat", "wrist rest"]
SAMPLE_PRODUCTS = [
    {
        "title": "Premium Ergonomic Desk Mat",
        "price": "EUR 24.99",
        "url": "https://www.amazon.com/dp/B001",
        "rating_stars": 4.3,
        "rating_count": 1247,
        "main_features": ["Non-slip base", "Extended 90x40cm size", "Waterproof surface"],
    },
    {
        "title": "Office Desk Pad Ultra",
        "price": "EUR 18.99",
        "url": "https://www.amazon.com/dp/B002",
        "rating_stars": 4.1,
        "rating_count": 893,
        "main_features": ["PU leather", "Double-sided", "Anti-slip"],
    },
]


@pytest.fixture
def step():
    return ProductResearchStep()


def test_step_id_is_product_research(step):
    assert step.step_id == "product_research"


def test_step_type_is_system_processing(step):
    assert step.step_type == "system_processing"


def test_component_type_is_product_list(step):
    assert step.component_type == "product_list"


@pytest.mark.asyncio
async def test_execute_yields_step_processing_first(step):
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=SAMPLE_PRODUCTS)), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    assert messages[0]["type"] == "step_processing"
    assert messages[0]["step_id"] == "product_research"


@pytest.mark.asyncio
async def test_execute_yields_step_result_with_products(step):
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=SAMPLE_PRODUCTS)), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    step_result = next((m for m in messages if m["type"] == "step_result"), None)
    assert step_result is not None
    assert "products" in step_result["data"]
    assert len(step_result["data"]["products"]) > 0


@pytest.mark.asyncio
async def test_execute_reads_keywords_from_run_get_output(step):
    """Step MUST use run.get_output(), not direct confirmed_outputs access."""
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    mock_get_output = run.get_output  # track calls via real method
    keywords_read = []

    original_get_output = run.get_output
    def tracking_get_output(step_id: str) -> dict:
        result = original_get_output(step_id)
        if step_id == "keyword_refinement":
            keywords_read.append(result)
        return result
    run.get_output = tracking_get_output

    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=SAMPLE_PRODUCTS)), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        await collect_step_messages(step, run)

    assert len(keywords_read) > 0, "Step did not call run.get_output('keyword_refinement')"


@pytest.mark.asyncio
async def test_execute_includes_source_keywords_in_result(step):
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=SAMPLE_PRODUCTS)), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    step_result = next((m for m in messages if m["type"] == "step_result"), None)
    assert step_result is not None
    assert "source_keywords" in step_result["data"]


@pytest.mark.asyncio
async def test_execute_emits_step_error_when_no_products_found(step):
    """Zero products must cause step_error (not crash)."""
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=[])), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    error_messages = [m for m in messages if m["type"] == "step_error"]
    assert len(error_messages) >= 1


@pytest.mark.asyncio
async def test_execute_zero_products_error_message_mentions_refine(step):
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=[])), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    error_msg = next(m for m in messages if m["type"] == "step_error")
    assert "No products" in error_msg["error"] or "refine" in error_msg["error"]


@pytest.mark.asyncio
async def test_execute_zero_products_error_is_not_retryable(step):
    """Zero products forces loop-back, not user-retry."""
    run = make_run(confirmed_outputs={"keyword_refinement": {"keywords": SAMPLE_KEYWORDS}})
    with patch("src.workflow.steps.s04_product_research.fetch_html", AsyncMock(return_value="<html></html>")), \
         patch("src.workflow.steps.s04_product_research.parse_marketplace_data",
               AsyncMock(return_value=[])), \
         patch("src.workflow.steps.s04_product_research.clean_html_for_llm", return_value="clean"):
        messages = await collect_step_messages(step, run)
    error_msg = next(m for m in messages if m["type"] == "step_error")
    assert error_msg["retryable"] is False
