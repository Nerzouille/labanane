"""Step 4 — Product Research (scraper + LLM parsing)."""
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, StepErrorMessage, ServerMessage
from src.logic.scraper import fetch_html, clean_html_for_llm, parse_marketplace_data

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput

SOURCES = ["Amazon", "Aliexpress", "eBay"]


async def _scrape_one(source: str, kw: str) -> list[dict]:
    """Scrape one source for a single keyword."""
    BASE_URLS = {
        "Amazon": "https://www.amazon.fr",
        "Aliexpress": "https://www.aliexpress.com",
        "eBay": "https://www.ebay.fr"
    }
    base_url = BASE_URLS.get(source, "")
    
    raw_html = await fetch_html(source, kw)
    clean_text = clean_html_for_llm(raw_html, base_url=base_url)
    items = await parse_marketplace_data(clean_text)
    
    for p in items:
        # Svelte front-end logic: Add source so the UI tag works better (optional but good)
        p["source"] = source
        
    return items


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

        results_tasks = [
            asyncio.create_task(_scrape_one(source, kw)) 
            for source in SOURCES
            for kw in keywords
        ]

        all_products: list[dict] = []
        seen: set[str] = set()
        
        for coro in asyncio.as_completed(results_tasks):
            try:
                items = await coro
                new_products = []
                for p in items:
                    key = p.get("url") or p.get("title")
                    if key and key not in seen:
                        seen.add(key)
                        new_products.append(p)
                        
                if new_products:
                    all_products.extend(new_products)
                    yield StepResultMessage(
                        step_id=self.step_id,
                        component_type=self.component_type,
                        data={
                            "products": all_products,
                            "source_keywords": source_keywords,
                            "is_final": False
                        },
                    )
            except Exception as e:
                import logging
                logging.error(f"Error scraping a source/keyword: {e}")

        if not all_products:
            yield StepErrorMessage(
                step_id=self.step_id,
                error="No products found — please refine your description.",
                retryable=False,
            )
            return

        # Final yield to indicate stream is complete
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "products": all_products,
                "source_keywords": source_keywords,
                "is_final": True
            },
        )
