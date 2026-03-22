"""Shared pytest fixtures for all test modules."""
from __future__ import annotations
import pytest
from src.workflow.run import WorkflowRun, StepOutput


# ── WorkflowRun factory ───────────────────────────────────────────────────


def make_run(
    description: str = "ergonomic desk mat for home office",
    confirmed_outputs: dict[str, dict] | None = None,
) -> WorkflowRun:
    """Build a WorkflowRun with pre-populated confirmed outputs."""
    run = WorkflowRun(run_id="test-run-id", total_steps=9, description=description)
    for step_id, data in (confirmed_outputs or {}).items():
        run.confirmed_outputs[step_id] = StepOutput(step_id=step_id, data=data)
    return run


# ── Sample data fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_product() -> dict:
    return {
        "title": "Premium Ergonomic Desk Mat",
        "price": "EUR 24.99",
        "url": "https://www.amazon.com/dp/B000TEST01",
        "rating_stars": 4.3,
        "rating_count": 1247,
        "main_features": ["Non-slip base", "Extended 90x40cm size", "Waterproof surface"],
    }


@pytest.fixture
def sample_products(sample_product) -> list[dict]:
    return [
        sample_product,
        {
            "title": "Office Desk Pad Ultra",
            "price": "EUR 18.99",
            "url": "https://www.amazon.com/dp/B000TEST02",
            "rating_stars": 4.1,
            "rating_count": 893,
            "main_features": ["Premium PU leather", "Double-sided", "Anti-slip"],
        },
        {
            "title": "Gaming Desk Mat XL",
            "price": "EUR 29.99",
            "url": "https://www.amazon.com/dp/B000TEST03",
            "rating_stars": 4.5,
            "rating_count": 3102,
            "main_features": ["RGB lighting", "500x1200mm", "Stitched edges"],
        },
    ]


@pytest.fixture
def sample_keywords() -> list[str]:
    return ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]


@pytest.fixture
def sample_trends(sample_keywords) -> dict:
    """MarketDataResult trends dict shape."""
    return {
        kw: {
            "interest_over_time": [{"date": "2025-03-01", "value": 72}],
            "interest_by_region": [{"geo": "US", "name": "United States", "value": 100}],
            "related_queries_top": [{"query": f"{kw} large", "value": 100}],
            "related_queries_rising": [{"query": f"best {kw}", "value": "+250%"}],
        }
        for kw in sample_keywords
    }


@pytest.fixture
def sample_ai_analysis() -> dict:
    return {
        "viability_score": 74,
        "go_no_go": "conditional",
        "summary": "Solid niche with moderate competition.",
        "analysis": "Demand is consistent year-round with a modest Q4 spike.",
        "key_risks": ["High competition from established brands", "Price pressure", "Seasonality"],
        "key_opportunities": ["Eco-friendly angle", "Bundle offers", "B2B market"],
        "criteria": [
            {"label": "Market size", "score": 80},
            {"label": "Competition", "score": 55},
            {"label": "Differentiation potential", "score": 70},
        ],
        "target_persona": {"description": "Remote workers aged 28-45 setting up a home office"},
        "differentiation_angles": {"content": "1. Bundle with cable management tray"},
        "competitive_overview": {"content": "Top competitors include Logitech Desk Mat"},
    }


@pytest.fixture
def run_with_keywords(sample_keywords) -> WorkflowRun:
    return make_run(
        confirmed_outputs={
            "keyword_confirmation": {"keywords": sample_keywords},
        }
    )


@pytest.fixture
def run_with_products(sample_keywords, sample_products) -> WorkflowRun:
    return make_run(
        confirmed_outputs={
            "keyword_confirmation": {"keywords": sample_keywords},
            "product_research": {"products": sample_products, "source_keywords": sample_keywords},
        }
    )


@pytest.fixture
def run_with_analysis(sample_keywords, sample_products, sample_trends, sample_ai_analysis) -> WorkflowRun:
    return make_run(
        confirmed_outputs={
            "keyword_confirmation": {"keywords": sample_keywords},
            "product_research": {"products": sample_products, "source_keywords": sample_keywords},
            "market_research": {
                "keywords": sample_keywords,
                "sources_available": ["google_trends"],
                "sources_unavailable": [],
                "trends": sample_trends,
            },
            "ai_analysis": sample_ai_analysis,
        }
    )


# ── Step output helpers ───────────────────────────────────────────────────


async def collect_step_messages(step, run: WorkflowRun, inp=None) -> list[dict]:
    """Collect all messages yielded by a step's execute() coroutine."""
    messages = []
    async for msg in step.execute(inp, run):
        messages.append(msg.model_dump())
    return messages
