"""Business logic — marketplace scraping and LLM-based parsing.

Pure functions only. No workflow state, no WebSocket access.
"""
from __future__ import annotations
import ast
import json
import os
import asyncio
from bs4 import BeautifulSoup
from pydantic import Field
from OpenHosta import emulate_async, config as openhosta_config
from src.config import settings
from src.models.report import Product, MarketAnalysis

openhosta_config.DefaultModel.api_key = settings.openai_api_key
openhosta_config.DefaultModel.model_name = settings.llm_model

MAX_TEXT_LENGTH = 30000


def clean_html_for_llm(raw_html: str) -> str:
    """Strip noise from HTML and inject href values so the LLM can extract URLs."""
    soup = BeautifulSoup(raw_html, "html.parser")
    for a in soup.find_all("a", href=True):
        if a.text.strip():
            a.string = f"{a.get_text(strip=True)} [URL: {a['href']}]"
    for tag in soup(["script", "style", "footer", "noscript", "svg"]):
        tag.extract()
    return soup.get_text(separator=" ", strip=True).replace("\xa0", " ")[:MAX_TEXT_LENGTH]


def _coerce_to_list_of_dicts(value: object) -> list[dict]:
    """Coerce emulate_async() output to list[dict].

    OpenHosta may return a string repr of a list instead of an actual list.
    """
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, str):
        stripped = value.strip()
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
        except (ValueError, SyntaxError):
            pass
    return []


async def parse_marketplace_data(cleaned_text: str) -> list[dict]:
    """
    Parse the cleaned text from a marketplace search page and extract ALL products.
    Each returned dict MUST contain exactly these keys:
      title (str), price (str), url (str),
      rating_stars (float), rating_range (int), rating_count (int),
      main_features (list of exactly 3 strings).
    """
    result = await emulate_async()
    return _coerce_to_list_of_dicts(result)


async def fetch_html(source: str, query: str) -> str:
    """Fetch raw HTML from a marketplace source for the given query.

    Handles rate-limiting with silent retry (up to 2 attempts, randomised delay).
    In production: uses httpx with browser-like headers.
    Currently: returns local test HTML for development.
    """
    await asyncio.sleep(1)
    file_path = os.path.join(
        os.path.dirname(__file__),
        "..", "tests", "scraper", "openhosta", "page_01.html"
    )
    if not os.path.exists(file_path):
        return f"<html><body><a href='http://mock_{source}'>{query} Mock Item</a> Price: $9.99</body></html>"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


async def generate_search_queries(product_description: str) -> list[str]:
    """
    Generate exactly 3 marketplace search keywords for the given product description.
    Returns a list of exactly 3 short keyword strings suitable for Amazon/Google Shopping.
    """
    return await emulate_async()


async def generate_market_analysis(
    product_description: str,
    products: list[dict],
    trends: dict,
) -> MarketAnalysis:
    """
    Analyse market viability using competitor products and trend data.
    Returns a fully populated MarketAnalysis including viability_score, go_no_go,
    summary, analysis, key_risks, key_opportunities, criteria (3-5),
    target_persona, differentiation_angles, competitive_overview.
    """
    result_dict = await emulate_async()
    return MarketAnalysis.model_validate(result_dict)
