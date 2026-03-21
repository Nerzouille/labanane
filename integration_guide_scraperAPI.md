# Guide d'Intégration du ScraperAPI dans la Pipeline

Salut ! 👋
Voici comment intégrer tes scripts de scraping ([dump_html_amazon.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/tests/scraper/scraps/dump_html_amazon.py), [dump_html_aliexpress.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/tests/scraper/scraps/dump_html_aliexpress.py), [dump_html_ebay.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/tests/scraper/scraps/dump_html_ebay.py)) directement dans le pipeline asynchrone du backend ([backend/src/scraper.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py)).

L'objectif est de remplacer le mock local actuel ([page_01.html](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/tests/scraper/openhosta/page_01.html)) par des requêtes HTTP asynchrones réelles vers ScraperAPI.

## 1. Préparation (Dépendances & ENV)

Dans FastAPI, le code est asynchrone. L'utilisation de `requests` bloque tout le serveur pendant le chargement internet. Il faut utiliser son équivalent asynchrone : **`httpx`** (déjà installé dans le projet via `uv`).

Assure-toi de rajouter la clé ScraperAPI dans le [.env](file:///home/nerzouille/Delivery/PoC/labanane/.env) à la racine :
```env
SCRAPERAPI_KEY="ta_cle_secrete_ici"
```

## 2. Remplacer [fetch_html](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py#55-75) dans [backend/src/scraper.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py)

Ouvre [backend/src/scraper.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py) et importe `httpx` et `os` au début du fichier. Remplace l'ancienne fonction [fetch_html](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py#55-75) (lignes de fin de fichier) par celle-ci :

```python
import httpx
import os

SCRAPERAPI_URL = "http://api.scraperapi.com"

async def fetch_html(source: str, query: str) -> str:
    """
    Récupère le code HTML d'une recherche sur un des marketplaces via ScraperAPI.
    Gère la construction d'URL dynamique selon la source (Amazon, Aliexpress, eBay).
    """
    api_key = os.getenv("SCRAPERAPI_KEY")
    if not api_key:
        print("⚠️ Warning: CLÉ SCRAPERAPI MANQUANTE ! Retourne une page vide.")
        return ""
        
    encoded_query = query.strip().replace(" ", "+")
    
    # 1. Constuire l'URL cible et les options en fonction de la source demandée
    target_url = ""
    render_js = "false"
    
    if source == "Amazon":
        target_url = f"https://www.amazon.fr/s?k={encoded_query}&page=1&language=fr_FR"
    elif source == "Aliexpress":
        target_url = f"https://www.aliexpress.com/wholesale?SearchText={encoded_query}&page=1&SortType=default"
        render_js = "true" # Requis pour Aliexpress d'après tes tests
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

    # 2. Exécuter la requête asynchrone via httpx
    # (httpx.AsyncClient est l'équivalent async non-bloquant de requests)
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Pour un hackathon, on garde ça simple sans boucle de try-except-sleep de 30 secondes, 
            # ScraperAPI s'occupe de réessayer de leur côté.
            response = await client.get(SCRAPERAPI_URL, params=params)
            response.raise_for_status()
            
            html = response.text
            
            # Sécurité anti-bot Aliexpress / eBay (basé sur tes scripts)
            if source in ["Aliexpress", "eBay"] and len(html) < 5000:
                print(f"⚠️ Contenu suspect ({len(html)} chars) pour {source} — probable page anti-bot")
                return ""
                
            return html
            
        except httpx.HTTPError as e:
            print(f"❌ Erreur HTTP lors du fetch {source}: {str(e)}")
            return ""
```

## 3. Mettre à jour les "Sources" dans [main.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/main.py)

Puisque tu as créé des scrapers pour Amazon, Aliexpress et eBay, il faut dire à l'API de taper sur ces sources au lieu des anciens mocks Google/Reddit.

Dans [backend/src/main.py](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/main.py), dans la route `def scrape_stream(...)`, trouve cette liste (vers la ligne 87) :
```python
    sources = ["Amazon", "Google Shopping", "Reddit"]
```
Et remplace-la par tes nouvelles sources exactes :
```python
    sources = ["Amazon", "Aliexpress", "eBay"]
```

## Bonus : Pourquoi `httpx` et pas `requests` ?
Quand la route 2 s'exécute (`/api/scrape-stream`), l'API lance toutes les sources *en parallèle* avec `asyncio.as_completed(tasks)`. Si tu utilises un basique `requests.get()` dans la fonction [fetch_html](file:///home/nerzouille/Delivery/PoC/labanane/backend/src/scraper.py#55-75), ton serveur web Python (FastAPI) entier va se mettre en pause sur *une* adresse (`threads=1`), ce qui tuera tout le principe du streaming asynchrone 🥲. \n \n En utilisant le code avec `async with httpx.AsyncClient`, les 3 sites sont récupérés à l'exacte même milliseconde !
