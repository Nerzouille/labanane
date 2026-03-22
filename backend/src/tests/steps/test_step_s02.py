"""Unit tests for Step 2 — KeywordRefinementStep."""
import pytest
from unittest.mock import AsyncMock, patch

from src.workflow.steps.s02_keyword_refinement import KeywordRefinementStep
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_KEYWORDS = ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]


@pytest.fixture
def step():
    return KeywordRefinementStep()


def test_step_id_is_keyword_refinement(step):
    assert step.step_id == "keyword_refinement"


def test_step_type_is_derivation(step):
    assert step.step_type == "derivation"


def test_component_type_is_keyword_list(step):
    assert step.component_type == "keyword_list"


def test_label_is_non_empty(step):
    assert isinstance(step.label, str)
    assert len(step.label) > 0


@pytest.mark.asyncio
async def test_execute_yields_step_processing_first(step):
    run = make_run(description="desk mats")
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)):
        messages = await collect_step_messages(step, run)
    assert messages[0]["type"] == "step_processing"


@pytest.mark.asyncio
async def test_execute_yields_step_result_second(step):
    run = make_run(description="desk mats")
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)):
        messages = await collect_step_messages(step, run)
    assert messages[1]["type"] == "step_result"


@pytest.mark.asyncio
async def test_execute_step_result_contains_keywords(step):
    run = make_run(description="desk mats")
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)):
        messages = await collect_step_messages(step, run)
    step_result = next(m for m in messages if m["type"] == "step_result")
    assert "keywords" in step_result["data"]
    assert step_result["data"]["keywords"] == SAMPLE_KEYWORDS


@pytest.mark.asyncio
async def test_execute_calls_generate_search_queries_with_description(step):
    run = make_run(description="ergonomic products for home office")
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)) as mock_gen:
        await collect_step_messages(step, run)
    mock_gen.assert_called_once_with("ergonomic products for home office")


@pytest.mark.asyncio
async def test_execute_step_result_step_id_is_keyword_refinement(step):
    run = make_run()
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)):
        messages = await collect_step_messages(step, run)
    step_result = next(m for m in messages if m["type"] == "step_result")
    assert step_result["step_id"] == "keyword_refinement"


@pytest.mark.asyncio
async def test_execute_component_type_is_keyword_list(step):
    run = make_run()
    with patch("src.workflow.steps.s02_keyword_refinement.generate_search_queries",
               AsyncMock(return_value=SAMPLE_KEYWORDS)):
        messages = await collect_step_messages(step, run)
    step_result = next(m for m in messages if m["type"] == "step_result")
    assert step_result["component_type"] == "keyword_list"
