"""
Amazon Scraper - ScraperAPI Edition (Anti-CAPTCHA)
====================================================
Utilise ScraperAPI pour contourner les protections Amazon.

▶ Inscription GRATUITE (5000 req) : https://www.scraperapi.com/
▶ Récupère ta clé API dans le dashboard et passe-la avec --apikey.

Champs extraits :
  - nom_produit, prix, revendeur, description
  - images (URLs séparées par |)
  - avis_note, avis_count, avis_details (failles produit)
  - mots_cles_references (ASIN + breadcrumbs + specs)
  - articles_associes
  - url_produit, asin

Usage :
  pip install requests beautifulsoup4 pandas lxml
  python amazon_scraper.py --query "abris de jardin" --pages 3 --apikey VOTRE_CLE
"""

import re
import csv
import json
import time
import random
import argparse
import urllib.parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

# ─── Configuration ─────────────────────────────────────────────────────────────

BASE_URL       = "https://www.amazon.fr"
SCRAPERAPI_URL = "http://api.scraperapi.com"
SCRAPERAPI_KEY = "COLLE_TA_CLE_ICI"   # ou passe --apikey en argument

CSV_FIELDS = [
    "nom_produit", "prix", "revendeur", "description",
    "images", "avis_note", "avis_count", "avis_details",
    "mots_cles_references", "articles_associes",
    "url_produit", "asin",
]

# ─── Helpers ───────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()

def extract_asin(url: str) -> str:
    m = re.search(r'/dp/([A-Z0-9]{10})', url)
    return m.group(1) if m else ""

def scraperapi_get(url: str, api_key: str, retries: int = 3) -> str:
    """Requête via ScraperAPI avec retry automatique."""
    payload = {
        "api_key": api_key,
        "url": url,
        "country_code": "fr",
    }
    for attempt in range(retries):
        try:
            resp = requests.get(SCRAPERAPI_URL, params=payload, timeout=60)
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 429:
                print(f"  ⏳ Rate limit ScraperAPI, attente 10s... (tentative {attempt+1})")
                time.sleep(10)
            elif resp.status_code == 403:
                print("  ❌ Clé API invalide ou quota épuisé (HTTP 403)")
                return ""
            else:
                print(f"  ⚠️ HTTP {resp.status_code} — tentative {attempt+1}/{retries}")
                time.sleep(5)
        except requests.RequestException as e:
            print(f"  ❌ Erreur réseau: {e} — tentative {attempt+1}/{retries}")
            time.sleep(5)
    return ""

# ─── Parsers ───────────────────────────────────────────────────────────────────

def parse_search_results(html: str) -> list:
    soup = BeautifulSoup(html, "lxml")
    products = []
    for div in soup.select('[data-component-type="s-search-result"]'):
        asin = div.get("data-asin", "").strip()
        link = div.select_one("h2 a")
        if not link or not asin:
            continue
        href = link.get("href", "")
        url = BASE_URL + href if href.startswith("/") else href
        url = re.sub(r'\?.*', '', url)
        if "/dp/" in url:
            products.append({"asin": asin, "url_produit": url})
    return products


def parse_product_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    data = {f: "" for f in CSV_FIELDS}
    data["url_produit"] = url
    data["asin"] = extract_asin(url)

    # Nom
    for sel in ["#productTitle", "#title span", "h1.a-size-large"]:
        el = soup.select_one(sel)
        if el:
            data["nom_produit"] = clean(el.get_text())
            break

    # Prix
    for sel in [".a-price .a-offscreen", "#priceblock_ourprice",
                "#priceblock_dealprice", "#price_inside_buybox",
                ".a-color-price", ".a-price-whole"]:
        el = soup.select_one(sel)
        if el:
            t = clean(el.get_text())
            if any(c.isdigit() for c in t):
                data["prix"] = t
                break

    # Revendeur
    for sel in ["#sellerProfileTriggerId", "#merchant-info a",
                "#tabular-buybox-truncate-1 .tabular-buybox-text span",
                ".offer-display-feature-text span"]:
        el = soup.select_one(sel)
        if el:
            data["revendeur"] = clean(el.get_text())
            break
    if not data["revendeur"]:
        for tag in soup.find_all(string=re.compile(r'Vendu par|Expédié et vendu', re.I)):
            parent = tag.find_parent()
            if parent:
                t = clean(parent.get_text())
                if t:
                    data["revendeur"] = t[:120]
                    break

    # Description
    parts = []
    for li in soup.select("#feature-bullets li span.a-list-item"):
        t = clean(li.get_text())
        if t and "Assurez-vous" not in t:
            parts.append(t)
    if not parts:
        for sel in ["#productDescription p", "#aplus p", "#aplus_feature_div p"]:
            for el in soup.select(sel):
                t = clean(el.get_text())
                if t:
                    parts.append(t)
    data["description"] = " | ".join(parts[:10])

    # Images
    images = []
    for pattern in [
        r'"colorImages"\s*:\s*\{\s*"initial"\s*:\s*(\[.*?\])\s*\}',
        r"'colorImages'\s*:\s*\{\s*'initial'\s*:\s*(\[.*?\])\s*\}",
        r'"imageGalleryData"\s*:\s*(\[.*?\])',
    ]:
        m = re.search(pattern, html, re.S)
        if m:
            try:
                for img in json.loads(m.group(1)):
                    for key in ["hiRes", "large", "thumb"]:
                        src = img.get(key, "")
                        if src and src not in images:
                            images.append(src)
                            break
            except Exception:
                pass
            if images:
                break
    if not images:
        for img_tag in soup.select("#imgTagWrapperId img, #altImages img, #imageBlock img"):
            src = (img_tag.get("src") or img_tag.get("data-src") or "").strip()
            if "images-amazon" in src and src not in images:
                src = re.sub(r'\._[A-Z]{2}\d+_', '._SL1500_', src)
                images.append(src)
    data["images"] = " | ".join(images[:8])

    # Note + compteur avis
    note_el = soup.select_one(
        "#acrPopover .a-size-base, "
        "#averageCustomerReviews .a-icon-alt, "
        "span[data-hook='rating-out-of-text']"
    )
    if note_el:
        data["avis_note"] = clean(note_el.get_text()).split(" ")[0].replace(",", ".")
    count_el = soup.select_one("#acrCustomerReviewText, #acrCustomerReviewLink span")
    if count_el:
        data["avis_count"] = clean(count_el.get_text())

    # Avis détaillés (texte complet → révèle les failles produit)
    reviews = []
    for rev in soup.select('[data-hook="review"]')[:8]:
        note_el  = rev.select_one('[data-hook="review-star-rating"] .a-icon-alt, [data-hook="cmps-review-star-rating"] .a-icon-alt')
        titre_el = rev.select_one('[data-hook="review-title"] span:not(.a-icon-alt)')
        corps_el = rev.select_one('[data-hook="review-body"] span')
        note  = clean(note_el.get_text()).split(" ")[0] if note_el else "?"
        titre = clean(titre_el.get_text()) if titre_el else ""
        corps = clean(corps_el.get_text()) if corps_el else ""
        if corps:
            reviews.append(f"[{note}★] {titre} — {corps[:400]}")
    data["avis_details"] = " || ".join(reviews)

    # Articles associés
    assoc = []
    for sel in ["#sims-consolidated-1 .a-link-normal", "#purchase-sims-feature .a-link-normal",
                "#bundle-v2-btf .a-link-normal", "[cel_widget_id^='MAIN-SIMS'] .a-link-normal"]:
        for el in soup.select(sel)[:6]:
            t = clean(el.get_text())
            if t and len(t) > 4:
                assoc.append(t)
    data["articles_associes"] = " | ".join(list(dict.fromkeys(assoc)))

    # Mots-clés / références
    kws = [data["asin"]]
    for el in soup.select("#wayfinding-breadcrumbs_feature_div a, .a-breadcrumb a"):
        t = clean(el.get_text())
        if t and t not in kws:
            kws.append(t)
    for row in soup.select(
        "#productDetails_techSpec_section_1 tr, "
        "#productDetails_detailBullets_sections1 tr, "
        "#detailBullets_feature_div li"
    ):
        th = row.select_one("th, .a-text-bold")
        td = row.select_one("td, span:not(.a-text-bold)")
        if th and td:
            kw = f"{clean(th.get_text())}:{clean(td.get_text())}"
            if kw not in kws:
                kws.append(kw)
    data["mots_cles_references"] = " | ".join(kws[:20])

    return data

# ─── Scraper principal ─────────────────────────────────────────────────────────

def scrape_amazon(query: str, max_pages: int, output_file: str, api_key: str):
    print(f"\n🚀 Amazon Scraper (ScraperAPI) — '{query}'")
    print(f"   Pages : {max_pages} | Output : {output_file}\n")

    product_urls = []
    for page_num in range(1, max_pages + 1):
        search_url = (
            f"{BASE_URL}/s?k={urllib.parse.quote_plus(query)}"
            f"&page={page_num}&language=fr_FR"
        )
        print(f"📄 Page {page_num}/{max_pages} → {search_url}")

        html = scraperapi_get(search_url, api_key)
        if not html:
            print("  ❌ Pas de réponse.")
            continue

        results = parse_search_results(html)
        if not results:
            print(f"  ⚠️ Aucun produit (fin des résultats?).")
            break

        existing = {p["url_produit"] for p in product_urls}
        new_ones = [r for r in results if r["url_produit"] not in existing]
        product_urls.extend(new_ones)
        print(f"  ✅ {len(new_ones)} nouveaux produits")
        time.sleep(random.uniform(1.0, 2.0))

    print(f"\n🔍 Total : {len(product_urls)} fiches produit")
    print("─" * 60)

    if not product_urls:
        print("❌ Aucune URL collectée. Vérifie ta clé API.")
        return

    all_products = []
    for i, prod in enumerate(product_urls, 1):
        url = prod["url_produit"]
        print(f"[{i:02d}/{len(product_urls)}] {url}")

        html = scraperapi_get(url, api_key)
        if not html:
            print("  ⚠️ Page vide, ignorée.")
            continue

        data = parse_product_page(html, url)
        if not data.get("nom_produit"):
            print("  ⚠️ Titre vide.")
            continue

        print(f"  ✓ {data['nom_produit'][:55]} | {data['prix']} | ⭐{data['avis_note']} ({data['avis_count']})")
        all_products.append(data)
        time.sleep(random.uniform(0.5, 1.5))

    if not all_products:
        print("\n❌ Aucun produit extrait.")
        return

    df = pd.DataFrame(all_products, columns=CSV_FIELDS)
    df.to_csv(output_file, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)

    print(f"\n{'='*60}")
    print(f"✅ {len(df)} produits exportés → {output_file}")
    print(f"{'='*60}\n")
    print(df[["nom_produit", "prix", "revendeur", "avis_note", "avis_count"]].head(5).to_string(index=False))

# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🛒 Amazon Scraper via ScraperAPI (anti-CAPTCHA)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Inscription gratuite ScraperAPI (5000 req) : https://www.scraperapi.com/

Exemples :
  python amazon_scraper.py --query "abris de jardin" --apikey MA_CLE
  python amazon_scraper.py --query "abris de jardin" --pages 5 --apikey MA_CLE --output jardins.csv
        """
    )
    parser.add_argument("--query",  "-q", required=True,  help="Mot-clé de recherche")
    parser.add_argument("--pages",  "-p", type=int, default=3, help="Pages de résultats (défaut: 3)")
    parser.add_argument("--output", "-o", default=None,   help="Fichier CSV de sortie")
    parser.add_argument("--apikey", "-k", default=None,   help="Clé API ScraperAPI")
    args = parser.parse_args()

    api_key = args.apikey or SCRAPERAPI_KEY
    if not api_key or api_key == "COLLE_TA_CLE_ICI":
        print("\n❌ Clé ScraperAPI manquante !")
        print("   1. Inscris-toi sur https://www.scraperapi.com/ (gratuit, 5000 req)")
        print("   2. Lance : python amazon_scraper.py --query '...' --apikey TA_CLE\n")
        return

    if args.output is None:
        slug = re.sub(r'[^a-z0-9]', '_', args.query.lower())
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"amazon_{slug}_{ts}.csv"

    scrape_amazon(args.query, args.pages, args.output, api_key)

if __name__ == "__main__":
    main()