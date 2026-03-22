"""Unit tests for Step 1 — ProductDescriptionStep."""
import pytest
from src.workflow.steps.s01_description import ProductDescriptionStep
from src.tests.conftest import make_run, collect_step_messages


@pytest.fixture
def step():
    return ProductDescriptionStep()


def test_step_id_is_product_description(step):
    assert step.step_id == "product_description"


def test_step_type_is_user_input(step):
    assert step.step_type == "user_input"


def test_label_is_non_empty(step):
    assert isinstance(step.label, str)
    assert len(step.label) > 0


def test_component_type_is_non_empty_string(step):
    assert isinstance(step.component_type, str)
    assert len(step.component_type) > 0


@pytest.mark.asyncio
async def test_execute_yields_at_least_one_message(step):
    run = make_run(description="ergonomic desk mats")
    messages = await collect_step_messages(step, run)
    assert len(messages) >= 1


@pytest.mark.asyncio
async def test_execute_yields_step_result_message(step):
    run = make_run(description="ergonomic desk mats")
    messages = await collect_step_messages(step, run)
    types = [m["type"] for m in messages]
    assert "step_result" in types


@pytest.mark.asyncio
async def test_execute_step_result_has_correct_step_id(step):
    run = make_run(description="ergonomic desk mats")
    messages = await collect_step_messages(step, run)
    step_result = next(m for m in messages if m["type"] == "step_result")
    assert step_result["step_id"] == "product_description"


@pytest.mark.asyncio
async def test_execute_no_step_processing_message(step):
    """user_input steps must NOT emit step_processing (no progress spinner)."""
    run = make_run(description="test")
    messages = await collect_step_messages(step, run)
    types = [m["type"] for m in messages]
    assert "step_processing" not in types
