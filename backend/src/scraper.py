"""Re-export shim — business logic has moved to src/logic/scraper.py."""
from src.logic.scraper import (  # noqa: F401
    clean_html_for_llm,
    parse_marketplace_data,
    fetch_html,
    generate_search_queries,
    generate_market_analysis,
)
from src.models.report import Product, MarketAnalysis  # noqa: F401
