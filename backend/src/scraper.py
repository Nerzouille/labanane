import os
import asyncio
import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from OpenHosta import emulate_async

MAX_TEXT_LENGTH = 30000
SCRAPERAPI_URL = "http://api.scraperapi.com"

class Product(BaseModel):
    title: str = Field(description="The full name of the product")
    price: str = Field(description="The price of the product, including currency, e.g. 'EUR 10.24'")
    rating_stars: float = Field(description="The average rating out of 5")
    rating_range: int = Field(description="The maximum rating (usually 5)")
    rating_count: int = Field(description="The total number of reviews")
    main_features: list[str] = Field(description="List of exactly 3 main features")
    url: str = Field(description="The absolute URL of the product page")

def clean_html_for_llm(raw_html: str, base_url: str = "") -> str:
    """Removes noise from HTML and injects links so the LLM can extract them."""
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # Inject href values into the text so the LLM can extract them
    for a in soup.find_all('a', href=True):
        if a.text.strip():
            href = a['href']
            # Make URL absolute if a base_url is provided and href is relative
            if base_url and href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)
                
            a.string = f"{a.get_text(strip=True)} [URL: {href}]"
            
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

async def generate_search_queries(product_description: str) -> list[str]:
    """
    Generate a list of the 3 best small research queries (key words) to find this product and all its variants on marketplaces like Amazon or Google Shopping.
    Return strictly a list of 3 strings.
    """
    return await emulate_async()

async def fetch_html(source: str, query: str) -> str:
    """
    Fetch the real HTML from the marketplace using ScraperAPI.
    """
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
            
            # Anti-bot check
            if source in ["Aliexpress", "eBay"] and len(html) < 5000:
                print(f"Anti-bot payload detected for {source} ({len(html)} chars).")
                return ""
                
            return html
            
        except httpx.HTTPError as e:
            print(f"HTTP Error fetching {source}: {e}")
            return ""
