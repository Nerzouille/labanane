"""Unit tests for Step 8 — PersonaGenerationStep."""
import pytest
from unittest.mock import AsyncMock, patch

from src.workflow.steps.s08_persona_generation import PersonaGenerationStep
from src.workflow.step_base import StepError
from src.models.report import Persona, PersonaSet
from src.tests.conftest import make_run, collect_step_messages

SAMPLE_KEYWORDS = ["ergonomic desk mat", "office mat"]
SAMPLE_PRODUCTS = [
    {"title": "Desk Mat", "price": "EUR 20", "url": "https://amazon.com/dp/B001",
     "rating_stars": 4.2, "rating_count": 500, "main_features": ["a", "b", "c"]},
]
SAMPLE_AI = {
    "viability_score": 74,
    "go_no_go": "conditional",
    "summary": "Solid niche.",
    "key_risks": ["Competition", "Price", "Seasonality"],
    "key_opportunities": ["Eco", "Bundle", "B2B"],
}
SAMPLE_PERSONA_SET = PersonaSet(personas=[
    Persona(name="The Weekend Creator", age_range="25–35",
            occupation="Freelance designer",
            motivations=["Professional look", "Aesthetic tools"],
            pain_points=["Cheap materials", "Wrong sizes"]),
    Persona(name="The Remote Professional", age_range="30–45",
            occupation="Software engineer",
            motivations=["Ergonomic surface", "Minimal design"],
            pain_points=["Mouse skip", "Cable mess"]),
    Persona(name="The Student Hustler", age_range="18–24",
            occupation="University student",
            motivations=["Gaming aesthetic", "Budget value"],
            pain_points=["Too expensive", "Too large"]),
])


@pytest.fixture
def step():
    return PersonaGenerationStep()


@pytest.fixture
def run_with_data():
    return make_run(confirmed_outputs={
        "keyword_confirmation": {"keywords": SAMPLE_KEYWORDS},
        "product_research": {"products": SAMPLE_PRODUCTS, "source_keywords": SAMPLE_KEYWORDS},
        "ai_analysis": SAMPLE_AI,
    })


def test_step_id_is_persona_generation(step):
    assert step.step_id == "persona_generation"


def test_step_type_is_system_processing(step):
    assert step.step_type == "system_processing"


def test_component_type_is_persona_generation(step):
    assert step.component_type == "persona_generation"


def test_label_is_persona_generation(step):
    assert step.label == "Persona Generation"


@pytest.mark.asyncio
async def test_execute_yields_step_processing_first(step, run_with_data):
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        messages = await collect_step_messages(step, run_with_data)
    assert messages[0]["type"] == "step_processing"


@pytest.mark.asyncio
async def test_execute_yields_step_result_with_persona_data(step, run_with_data):
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        messages = await collect_step_messages(step, run_with_data)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert sr["component_type"] == "persona_generation"


@pytest.mark.asyncio
async def test_execute_step_result_data_has_personas_array(step, run_with_data):
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        messages = await collect_step_messages(step, run_with_data)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert "personas" in sr["data"]
    assert isinstance(sr["data"]["personas"], list)


@pytest.mark.asyncio
async def test_execute_step_result_personas_has_3_items(step, run_with_data):
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        messages = await collect_step_messages(step, run_with_data)
    sr = next(m for m in messages if m["type"] == "step_result")
    assert len(sr["data"]["personas"]) == 3


@pytest.mark.asyncio
async def test_execute_raises_step_error_when_no_products_and_no_ai_analysis(step):
    run_empty = make_run(confirmed_outputs={})
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        with pytest.raises(StepError) as exc_info:
            await collect_step_messages(step, run_empty)
    assert exc_info.value.retryable is False


@pytest.mark.asyncio
async def test_execute_step_processing_step_id_matches(step, run_with_data):
    with patch("src.workflow.steps.s08_persona_generation.generate_personas",
               AsyncMock(return_value=SAMPLE_PERSONA_SET)):
        messages = await collect_step_messages(step, run_with_data)
    proc = next(m for m in messages if m["type"] == "step_processing")
    assert proc["step_id"] == "persona_generation"
