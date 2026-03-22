"""Unit tests for Step 5 — ProductValidationStep."""
import pytest
from src.workflow.steps.s05_product_validation import ProductValidationStep
from src.tests.conftest import make_run, collect_step_messages


@pytest.fixture
def step():
    return ProductValidationStep()


def test_step_id_is_product_validation(step):
    assert step.step_id == "product_validation"


def test_step_type_is_confirmation(step):
    assert step.step_type == "confirmation"


def test_component_type_is_confirmation(step):
    assert step.component_type == "confirmation"


def test_label_is_non_empty(step):
    assert isinstance(step.label, str)
    assert len(step.label) > 0


@pytest.mark.asyncio
async def test_execute_yields_confirmation_request(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    types = [m["type"] for m in messages]
    assert "confirmation_request" in types


@pytest.mark.asyncio
async def test_execute_confirmation_request_step_id(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    cr = next(m for m in messages if m["type"] == "confirmation_request")
    assert cr["step_id"] == "product_validation"


@pytest.mark.asyncio
async def test_execute_confirmation_request_has_prompt(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    cr = next(m for m in messages if m["type"] == "confirmation_request")
    assert "prompt" in cr["data"]
    assert len(cr["data"]["prompt"]) > 0


@pytest.mark.asyncio
async def test_execute_no_step_processing(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    assert all(m["type"] != "step_processing" for m in messages)
