import os
import json
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from OpenHosta import emulate

MAX_TEXT_LENGTH = 30000

class Product(BaseModel):
    title: str = Field(description="The full name of the product")
    price: str = Field(description="The price of the product, including currency, e.g. 'EUR 10.24'")
    rating_stars: float = Field(description="The average rating out of 5")
    rating_range: int = Field(description="The maximum rating (usually 5)")
    rating_count: int = Field(description="The total number of reviews")
    main_features: list[str] = Field(description="List of exactly 3 main features")
    url: str = Field(description="The absolute URL of the product page")

def parse_marketplace_data(cleaned_text: str) -> list[dict]:
    """
    Parse the cleaned text from a marketplace search page and extract ALL product information found.
    You MUST extract every single product present in the text, do not limit yourself to 3.
    The returned list of dictionaries must strictly contain the following keys:
    - title (str): The full name of the product
    - price (str): The price of the product, including currency, e.g. 'EUR 10.24'
    - rating_stars (float): The average rating out of 5
    - rating_range (int): The maximum rating (usually 5)
    - rating_count (int): The total number of reviews
    - main_features (list of 3 string elements): List of exactly 3 main features
    - url (str): The absolute URL of the product page
    """
    return emulate()

def main():
    file_path = os.path.join(os.path.dirname(__file__), "page_01.html")
    # file_path = os.path.join(os.path.dirname(__file__), "Amazon.com _ red cat t-shirt.html")
    
    with open(file_path, "r", encoding="utf-8") as file:
        raw_html_string = file.read()
            
    soup = BeautifulSoup(raw_html_string, "html.parser")
    
    # Inject href values into the text so the LLM can extract them
    for a in soup.find_all('a', href=True):
        if a.text.strip():
            # Append the URL right after the link text
            a.string = f"{a.get_text(strip=True)} [URL: {a['href']}]"
            
    for noise_tag in soup(["script", "style", "footer", "noscript", "svg"]):
        noise_tag.extract()
        
    clean_text = soup.get_text(separator=" ", strip=True).replace("\xa0", " ")
    text_to_analyze = clean_text[:MAX_TEXT_LENGTH]
    
    raw_dicts = parse_marketplace_data(text_to_analyze)
    
    valid_products = []
    for item in raw_dicts:
        try:
            valid_products.append(Product(**item))
        except Exception as e:
            print(f"Skipping invalid item: {item}\nReason: {e}\n")
            
    print(f"✅ Extracted {len(valid_products)} valid products!\n")
    
    output_file = os.path.join(os.path.dirname(__file__), "extracted_products.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json_data = [p.model_dump() for p in valid_products]
        json.dump(json_data, f, indent=2, ensure_ascii=False)
        
    print(f"📁 Saved all products to {output_file}")

if __name__ == "__main__":
    main()