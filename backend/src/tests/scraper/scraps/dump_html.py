"""
Multi-Marketplace HTML Dumper
==============================
Dump N pages de résultats Amazon + Aliexpress + eBay en un seul fichier HTML par page.
Chaque fichier contient le HTML brut des 3 sources à la suite.

Usage :
  python dump_html.py --query "abris de jardin" --pages 50 --apikey TA_CLE

Structure de sortie :
  html_dump/
  ├── page_01.html   ← Amazon + Aliexpress + eBay page 1
  ├── page_02.html   ← Amazon + Aliexpress + eBay page 2
  └── ...
"""

import os
import random
import argparse
import asyncio
import httpx

SCRAPERAPI_URL = "http://api.scraperapi.com"
SOURCES = ["amazon", "aliexpress", "ebay"]


# ---------------------------------------------------------------------------
# Construction des URLs
# ---------------------------------------------------------------------------

def build_url(source: str, query: str, page_num: int) -> str:
    encoded = query.strip().replace(" ", "+")
    if source == "amazon":
        return f"https://www.amazon.fr/s?k={encoded}&page={page_num}&language=fr_FR"
    elif source == "aliexpress":
        return f"https://www.aliexpress.com/wholesale?SearchText={encoded}&page={page_num}&SortType=default"
    elif source == "ebay":
        return f"https://www.ebay.fr/sch/i.html?_nkw={encoded}&_pgn={page_num}&_ipg=60"
    raise ValueError(f"Source inconnue : {source}")


def scraper_params(source: str, api_key: str, target_url: str) -> dict:
    params = {"api_key": api_key, "url": target_url, "country_code": "fr"}
    if source == "aliexpress":
        params["render"] = "true"  # JS rendering requis pour Aliexpress
    return params


# ---------------------------------------------------------------------------
# Fetch asynchrone
# ---------------------------------------------------------------------------

async def fetch(client: httpx.AsyncClient, source: str, api_key: str, url: str) -> str:
    for attempt in range(3):
        try:
            resp = await client.get(SCRAPERAPI_URL, params=scraper_params(source, api_key, url))
            if resp.status_code == 200:
                html = resp.text
                if len(html) < 5_000:
                    print(f"  ⚠️  [{source}] Contenu suspect ({len(html):,} chars) — probable anti-bot")
                    return ""
                return html
            wait = 10 * (attempt + 1)
            print(f"  ⚠️  [{source}] HTTP {resp.status_code} (tentative {attempt+1}/3) — attente {wait}s")
            await asyncio.sleep(wait)
        except httpx.HTTPError as e:
            wait = 10 * (attempt + 1)
            print(f"  ❌  [{source}] {e} (tentative {attempt+1}/3) — attente {wait}s")
            await asyncio.sleep(wait)
    return ""


# ---------------------------------------------------------------------------
# Fetch des 3 sources en parallèle pour une page donnée
# ---------------------------------------------------------------------------

async def fetch_all_sources(client: httpx.AsyncClient, query: str, page_num: int, api_key: str) -> dict[str, str]:
    tasks = {
        source: fetch(client, source, api_key, build_url(source, query, page_num))
        for source in SOURCES
    }
    results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

async def main_async(args: argparse.Namespace) -> None:
    os.makedirs(args.outdir, exist_ok=True)
    print(f"\n🚀 Dump HTML — '{args.query}' — {args.pages} pages — sources : {', '.join(SOURCES)}")
    print(f"   Sortie → ./{args.outdir}/\n")

    ok = fail = 0

    async with httpx.AsyncClient(timeout=120.0) as client:
        for page_num in range(1, args.pages + 1):
            print(f"[{page_num:02d}/{args.pages}] Fetch des 3 sources ... ", end="", flush=True)

            results = await fetch_all_sources(client, args.query, page_num, args.apikey)

            # On concatène les 3 blocs HTML avec un séparateur lisible
            combined = ""
            for source, html in results.items():
                combined += f"\n\n<!-- ═══════════ SOURCE : {source.upper()} | PAGE {page_num} ═══════════ -->\n\n"
                combined += html if html else f"<!-- ❌ Aucun contenu récupéré pour {source} -->"

            fname = os.path.join(args.outdir, f"page_{page_num:02d}.html")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(combined)

            sources_ok = [s for s, h in results.items() if h]
            sources_ko = [s for s, h in results.items() if not h]
            print(f"✅ {', '.join(sources_ok) or '—'}  ❌ {', '.join(sources_ko) or '—'}  → {fname}")

            ok += 1
            await asyncio.sleep(random.uniform(1, 2.5))

    print(f"\n{'='*55}")
    print(f"✅ {ok} fichiers sauvegardés | ❌ {fail} échecs")
    print(f"📁 Dossier : ./{args.outdir}/")
    print(f"{'='*55}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Marketplace HTML Dumper via ScraperAPI")
    parser.add_argument("--query",  "-q", required=True,        help="Mot-clé de recherche")
    parser.add_argument("--pages",  "-p", type=int, default=50, help="Nombre de pages (défaut: 50)")
    parser.add_argument("--apikey", "-k", required=True,        help="Clé API ScraperAPI")
    parser.add_argument("--outdir", "-o", default="html_dump",  help="Dossier de sortie (défaut: html_dump)")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()