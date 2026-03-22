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

openhosta_config.DefaultModel.api_key = settings.openai_api_key or os.getenv("OPENHOSTA_DEFAULT_MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
openhosta_config.DefaultModel.model_name = settings.llm_model or os.getenv("OPENHOSTA_DEFAULT_MODEL_NAME") or "gpt-4o-mini"

MAX_TEXT_LENGTH = 30000


def clean_html_for_llm(raw_html: str, base_url: str = "") -> str:
    """Strip noise from HTML and inject href values so the LLM can extract URLs."""
    soup = BeautifulSoup(raw_html, "html.parser")
    for a in soup.find_all("a", href=True):
        if a.text.strip():
            href = a['href']
            if base_url and href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
            a.string = f"{a.get_text(strip=True)} [URL: {href}]"
    for img in soup.find_all("img", src=True):
        img.string = f"[IMG: {img['src']}]"
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
      main_features (list of exactly 3 strings),
      image_url (str | None): direct URL to the product image from [IMG: ...] markers, or null if not found.
    """
    result = await emulate_async()
    return _coerce_to_list_of_dicts(result)


async def fetch_html(source: str, query: str) -> str:
    """Fetch raw HTML from a marketplace using ScraperAPI."""
    import httpx
    
    SCRAPERAPI_URL = "http://api.scraperapi.com"
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key:
        print("Missing SCRAPERAPI_KEY in environment. Returning empty string.")
        return ""
        
    encoded_query = query.strip().replace(" ", "+")
    target_url = ""
    render_js = "false"
    
    if source == "Amazon":
        target_url = f"https://www.amazon.fr/s?k={encoded_query}&page=1&language=fr_FR"
    elif source == "Aliexpress":
        target_url = f"https://www.aliexpress.com/wholesale?SearchText={encoded_query}&page=1&SortType=default"
        render_js = "true"
    elif source == "eBay":
        target_url = f"https://www.ebay.fr/sch/i.html?_nkw={encoded_query}&_pgn=1&_ipg=60"
    else:
        return ""

    params = {
        "api_key": api_key,
        "url": target_url,
        "country_code": "fr",
        "render": render_js
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.get(SCRAPERAPI_URL, params=params)
            response.raise_for_status()
            
            html = response.text
            if source in ["Aliexpress", "eBay"] and len(html) < 5000:
                print(f"Anti-bot payload detected for {source} ({len(html)} chars).")
                return ""
            return html
        except httpx.HTTPError as e:
            print(f"HTTP Error fetching {source}: {e}")
            return ""


async def generate_search_queries(product_description: str) -> list[str]:
    """
    Generate exactly 3 marketplace search keywords for the given product description.
    Returns a list of exactly 3 short keyword strings suitable for Amazon/Google Shopping.
    """
    import ast
    result = await emulate_async()
    
    if isinstance(result, list):
        return [str(item) for item in result]
        
    if isinstance(result, str):
        stripped = result.strip()
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (ValueError, SyntaxError):
            cleaned = stripped.strip("[]").split(",")
            return [x.strip(" '\"") for x in cleaned if x.strip()]
            
    return []


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
