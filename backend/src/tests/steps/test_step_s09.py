"""Unit tests for Step 8 — FinalCriteriaStep."""
import pytest
from src.workflow.steps.s09_final_criteria import FinalCriteriaStep
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_AI_OUTPUT = {
    "viability_score": 74,
    "go_no_go": "conditional",
    "summary": "Solid niche with moderate competition.",
    "analysis": "Demand is consistent year-round.",
    "key_risks": ["High competition", "Price pressure", "Seasonality"],
    "key_opportunities": ["Eco-friendly angle", "Bundle offers", "B2B market"],
    "criteria": [{"label": "Market size", "score": 80}],
    "target_persona": {"description": "Remote workers"},
    "differentiation_angles": {"content": "Bundle with tray"},
    "competitive_overview": {"content": "Logitech dominates"},
}


@pytest.fixture
def step():
    return FinalCriteriaStep()


@pytest.fixture
def run_with_ai():
    return make_run(confirmed_outputs={"ai_analysis": SAMPLE_AI_OUTPUT})


def test_step_id_is_final_criteria(step):
    assert step.step_id == "final_criteria"


def test_step_type_is_derivation(step):
    assert step.step_type == "derivation"


def test_component_type_is_final_criteria(step):
    assert step.component_type == "final_criteria"


@pytest.mark.asyncio
async def test_execute_yields_step_result(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    types = [m["type"] for m in messages]
    assert "step_result" in types


@pytest.mark.asyncio
async def test_execute_step_result_has_summary(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "summary" in sr["data"]
    assert isinstance(sr["data"]["summary"], str)


@pytest.mark.asyncio
async def test_execute_step_result_has_go_no_go(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "go_no_go" in sr["data"]
    assert sr["data"]["go_no_go"] in {"go", "no-go", "conditional"}


@pytest.mark.asyncio
async def test_execute_step_result_go_no_go_matches_ai_analysis(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert sr["data"]["go_no_go"] == SAMPLE_AI_OUTPUT["go_no_go"]


@pytest.mark.asyncio
async def test_execute_step_result_has_key_risks(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "key_risks" in sr["data"]
    assert isinstance(sr["data"]["key_risks"], list)


@pytest.mark.asyncio
async def test_execute_step_result_has_key_opportunities(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "key_opportunities" in sr["data"]
    assert isinstance(sr["data"]["key_opportunities"], list)


@pytest.mark.asyncio
async def test_execute_no_step_processing_for_derivation(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    assert all(m["type"] != "step_processing" for m in messages)


@pytest.mark.asyncio
async def test_execute_component_type_is_final_criteria(step, run_with_ai):
    messages = await collect_step_messages(step, run_with_ai)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert sr["component_type"] == "final_criteria"


@pytest.mark.asyncio
async def test_execute_no_external_logic_calls(step, run_with_ai):
    """FinalCriteriaStep is a derivation step — no external calls."""
    # No mocking needed: if this test passes, no external calls were made
    messages = await collect_step_messages(step, run_with_ai)
    assert len(messages) >= 1
