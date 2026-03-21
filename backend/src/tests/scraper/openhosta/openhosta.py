from OpenHosta import emulate, emulate_async
import asyncio

def generate_search_queries(product_description: str) -> list[str]:
    """Generate a list of the 3 best small research queries (key words) to find this product and all its variants on marketplaces like Amazon or Google Shopping"""
    return emulate()

async def capitalize_cities(sentence: str) -> str:
    """Capitalize the first letter of all city names in a sentence."""
    return await emulate_async()

print(asyncio.run(capitalize_cities("je suis allé à paris puis marseille lyon et même une fois à florence en italie pendant que mon papa mangeait du caviar de los angeles à new york avec ma seour sudédoise et mon gros caca qui pue des fesses sur une ile paradisiaques du large de la roumanie près des îles du japon")))

def parse_marketplace_data(raw_html_or_text: str) -> list[dict]:
    """Parse the raw scraped HTML from the marketplace. Return a list of dicts: title, price_range, real_url, main_features."""
    return emulate()

def search_products_links(search_queries: list[str]) -> str:
    """Search for the given search queries links of articles on marketplaces like Amazon or Google Shopping. I don't want a reasearch query on these website, but really the product link"""
    return emulate()

def parse_marketplace_data(raw_scraped_data: str) -> list[dict]:
    """Parse the raw scraped data from the marketplace and return a list of dictionaries with the following keys: title, price_range, url, main_features (list of the 3 main features of the product)"""
    return emulate()
    

# print(generate_search_queries("A red t-shirt with a picture of a cat on it"))
# print(read_produdct_datas("https://www.amazon.com/BLACKOO-Women-Graphic-T-Shirts-Small/dp/B0F3CYQXZX/ref=sr_1_6"))
# print(search_products_links(generate_search_queries("A red t-shirt with a picture of a cat on it")))
# print(parse_marketplace_data("https://www.amazon.fr/s?k=red+t-shirt+with+a+picture+of+a+cat+on+it"))