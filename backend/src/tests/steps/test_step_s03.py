"""Unit tests for Step 3 — KeywordConfirmationStep."""
import pytest
from src.workflow.steps.s03_keyword_confirmation import KeywordConfirmationStep
from src.tests.conftest import make_run, collect_step_messages


@pytest.fixture
def step():
    return KeywordConfirmationStep()


def test_step_id_is_keyword_confirmation(step):
    assert step.step_id == "keyword_confirmation"


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
async def test_execute_confirmation_request_has_correct_step_id(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    cr = next(m for m in messages if m["type"] == "confirmation_request")
    assert cr["step_id"] == "keyword_confirmation"


@pytest.mark.asyncio
async def test_execute_confirmation_request_has_prompt(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    cr = next(m for m in messages if m["type"] == "confirmation_request")
    assert "prompt" in cr["data"]
    assert isinstance(cr["data"]["prompt"], str)
    assert len(cr["data"]["prompt"]) > 0


@pytest.mark.asyncio
async def test_execute_confirmation_request_component_type_is_confirmation(step):
    run = make_run()
    messages = await collect_step_messages(step, run)
    cr = next(m for m in messages if m["type"] == "confirmation_request")
    assert cr["component_type"] == "confirmation"


@pytest.mark.asyncio
async def test_execute_no_step_processing_message(step):
    """Confirmation steps do not emit step_processing."""
    run = make_run()
    messages = await collect_step_messages(step, run)
    types = [m["type"] for m in messages]
    assert "step_processing" not in types
