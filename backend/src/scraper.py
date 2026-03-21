import os
import asyncio
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from OpenHosta import emulate_async, config as openhosta_config
from src.config import settings

openhosta_config.DefaultModel.api_key = settings.openai_api_key
openhosta_config.DefaultModel.model_name = settings.llm_model

MAX_TEXT_LENGTH = 30000

class Product(BaseModel):
    title: str = Field(description="The full name of the product")
    price: str = Field(description="The price of the product, including currency, e.g. 'EUR 10.24'")
    rating_stars: float = Field(description="The average rating out of 5")
    rating_range: int = Field(description="The maximum rating (usually 5)")
    rating_count: int = Field(description="The total number of reviews")
    main_features: list[str] = Field(description="List of exactly 3 main features")
    url: str = Field(description="The absolute URL of the product page")

def clean_html_for_llm(raw_html: str) -> str:
    """Removes noise from HTML and injects links so the LLM can extract them."""
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Inject href values into the text so the LLM can extract them
    for a in soup.find_all('a', href=True):
        if a.text.strip():
            a.string = f"{a.get_text(strip=True)} [URL: {a['href']}]"
            
    for noise_tag in soup(["script", "style", "footer", "noscript", "svg"]):
        noise_tag.extract()
        
    clean_text = soup.get_text(separator=" ", strip=True).replace("\xa0", " ")
    return clean_text[:MAX_TEXT_LENGTH]

async def parse_marketplace_data(cleaned_text: str) -> list[dict]:
    """
    Parse the cleaned text from a marketplace search page and extract ALL product information found.
    You MUST extract every single product present in the text, do not limit yourself to 3.
    The returned list of dictionaries must strictly contain the following keys:
    - title (str)
    - price (str)
    - rating_stars (float)
    - rating_range (int)
    - rating_count (int)
    - main_features (list of 3 string elements)
    - url (str)
    """
    return await emulate_async()

class Criterion(BaseModel):
    label: str = Field(description="Criterion name, e.g. 'Market size'")
    score: int = Field(description="Score from 0 to 100")

class MarketAnalysis(BaseModel):
    viability_score: int = Field(description="Overall market viability score from 0 to 100")
    go_no_go: str = Field(description="Final decision: exactly one of 'go', 'no-go', or 'conditional'")
    summary: str = Field(description="One-sentence market verdict")
    analysis: str = Field(description="2-3 sentence market analysis covering demand, competition and positioning")
    key_risks: list[str] = Field(description="Top 3 risks as short bullet strings")
    key_opportunities: list[str] = Field(description="Top 3 opportunities as short bullet strings")
    criteria: list[Criterion] = Field(description="3 to 5 scoring criteria each with a label and a score 0-100")

async def generate_market_analysis(product_description: str, products: list[dict]) -> dict:
    """
    Analyse the market viability for the given product idea using the list of competitor products found on marketplaces.
    Return a dict with keys: viability_score (int 0-100), go_no_go (str: 'go', 'no-go', or 'conditional'),
    summary (str), analysis (str), key_risks (list[str]), key_opportunities (list[str]),
    criteria (list of dicts with 'label' (str) and 'score' (int 0-100) keys).
    """
    return await emulate_async()

async def generate_search_queries(product_description: str) -> list[str]:
    """
    Generate a list of the 3 best small research queries (key words) to find this product and all its variants on marketplaces like Amazon or Google Shopping.
    Return strictly a list of 3 strings.
    """
    return await emulate_async()

async def fetch_html(source: str, query: str) -> str:
    """
    Mock fetcher that returns the content of the local page_01.html file.
    In the future, this will use httpx/requests to fetch from actual sources.
    #TODO: implement actual fetcher for Amazon, and others
    """
    # Simulate network delay for fetching
    await asyncio.sleep(1)
    
    file_path = os.path.join(
        os.path.dirname(__file__), 
        "tests", "scraper", "openhosta", "page_01.html"
    )
    
    # If file isn't found, return a basic fake page
    if not os.path.exists(file_path):
        return f"<html><body><a href='http://mock_{source}'>{query} Mock Item</a> Price: $9.99</body></html>"
        
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
