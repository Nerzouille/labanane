import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from src.scraper import (
    fetch_html, 
    clean_html_for_llm, 
    parse_marketplace_data, 
    generate_search_queries
)

# Force le chargement du .env situé dans le même dossier que ce script (backend/.env)
env_path = Path(__file__).parent / ".env"
print(f"🔍 Recherche du fichier .env ici : {env_path}")

if env_path.exists():
    print(f"✅ Fichier .env trouvé !")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"❌ Fichier .env NON TROUVÉ à cet endroit.")
    # On essaie quand même le load_dotenv par défaut au cas où
    load_dotenv()

async def test_minimal_pipeline():
    # Petit check des clés après chargement
    s_key = os.getenv("SCRAPERAPI_KEY")
    o_key = os.getenv("OPENHOSTA_API_KEY")
    
    print(f"📊 Diagnostic des clés :")
    print(f"   - SCRAPERAPI_KEY : {'Présente ✅' if s_key else 'MANQUANTE ❌'}")
    print(f"   - OPENHOSTA_API_KEY : {'Présente ✅' if o_key else 'MANQUANTE ❌'}")
    
    if not s_key or not o_key:
        print("\nArrêt du test : clés manquantes.")
        return

    # 1. TEST RECHERCHE (Génération de mots-clés)
    description = "Abris de jardin en bois traité autoclave"
    print(f"--- 1. Recherche : {description} ---")
    
    # Assure-toi que OPENHOSTA_API_KEY est bien définie en variable d'env
    queries = await generate_search_queries(description)
    print(f"✅ Mots-clés IA générés : {queries}")

    if not queries:
        print("❌ Aucun mot-clé généré")
        return

    # 2. TEST SCRAPPING (Fetch + Parse)
    # On teste sur une seule source (Amazon) avec le premier mot-clé pour gagner du temps
    source = "Amazon"
    query = queries[0]
    print(f"\n--- 2. Scrapping {source} pour : {query} ---")
    
    # URL de base pour reconstruire les liens absolus
    BASE_URLS = {
        "Amazon": "https://www.amazon.fr",
        "Aliexpress": "https://www.aliexpress.com",
        "eBay": "https://www.ebay.fr"
    }
    base_url = BASE_URLS.get(source, "")

    # Récupération du HTML via ScraperAPI
    html = await fetch_html(source, query)
    
    if not html:
        print(f"❌ Impossible de récupérer du contenu pour {source}")
        return
        
    print(f"✅ HTML reçu ({len(html)} caractères)")

    # Nettoyage et Extraction via OpenHosta
    clean_text = clean_html_for_llm(html, base_url=base_url)
    print(f"✅ Texte nettoyé avec URLs absolues pour l'IA")
    
    print("⏳ Extraction des produits par l'IA...")
    products = await parse_marketplace_data(clean_text)
    
    if products:
        print(f"✅ {len(products)} produits extraits !")
        # Sauvegarde pour vérification manuelle
        output_file = Path(__file__).parent / "debug_products.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        print(f"💾 Les {len(products)} produits ont été sauvegardés dans : {output_file}")
        
        for i, p in enumerate(products):
            print(f"   [{i+1}] {p['title']} - {p['price']}")
            print(f"       🔗 URL: {p['url']}")
    else:
        print("❌ Aucun produit extrait. Le contenu HTML est peut-être invalide.")

if __name__ == "__main__":
    asyncio.run(test_minimal_pipeline())
