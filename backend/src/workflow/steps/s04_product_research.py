"""Step 4 — Product Research (scraper + LLM parsing)."""
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, StepErrorMessage, ServerMessage
from src.logic.scraper import fetch_html, clean_html_for_llm, parse_marketplace_data

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput

SOURCES = ["Amazon", "Google Shopping"]


async def _scrape_source(source: str, keywords: list[str]) -> list[dict]:
    """Scrape one source for all keywords, deduplicating by URL."""
    products: list[dict] = []
    seen: set[str] = set()
    for kw in keywords:
        raw_html = await fetch_html(source, kw)
        clean_text = clean_html_for_llm(raw_html)
        items = await parse_marketplace_data(clean_text)
        for p in items:
            key = p.get("url") or p.get("title")
            if key and key not in seen:
                seen.add(key)
                products.append(p)
    return products


class ProductResearchStep(Step):
    @property
    def step_id(self) -> str:
        return "product_research"

    @property
    def label(self) -> str:
        return "Product Research"

    @property
    def step_type(self) -> str:
        return "system_processing"

    @property
    def component_type(self) -> str:
        return "product_list"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)

        keywords: list[str] = run.get_output("keyword_refinement").get("keywords", [])
        if not keywords and input:
            keywords = input.data.get("keywords", [])

        source_keywords = keywords

        results = await asyncio.gather(
            *[_scrape_source(source, keywords) for source in SOURCES],
            return_exceptions=True,
        )

        all_products: list[dict] = []
        for r in results:
            if isinstance(r, list):
                all_products.extend(r)

        if not all_products:
            yield StepErrorMessage(
                step_id=self.step_id,
                error="No products found — please refine your description.",
                retryable=False,
            )
            return

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={"products": all_products, "source_keywords": source_keywords},
        )
