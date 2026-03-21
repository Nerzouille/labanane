"""
Amazon HTML Dumper
==================
Dump N pages de résultats Amazon en fichiers HTML bruts.

Usage :
  python dump_html.py --query "abris de jardin" --pages 50 --apikey TA_CLE
"""

import os
import time
import random
import argparse
import requests

SCRAPERAPI_URL = "http://api.scraperapi.com"
BASE_URL       = "https://www.amazon.fr"

def fetch(url: str, api_key: str) -> str:
    for attempt in range(3):
        try:
            resp = requests.get(
                SCRAPERAPI_URL,
                params={"api_key": api_key, "url": url, "country_code": "fr"},
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.text
            print(f"  ⚠️ HTTP {resp.status_code} (tentative {attempt+1}/3)")
            time.sleep(5)
        except Exception as e:
            print(f"  ❌ Erreur: {e} (tentative {attempt+1}/3)")
            time.sleep(5)
    return ""

def main():
    parser = argparse.ArgumentParser(description="Amazon HTML Dumper via ScraperAPI")
    parser.add_argument("--query",  "-q", required=True,            help="Mot-clé de recherche")
    parser.add_argument("--pages",  "-p", type=int, default=50,     help="Nombre de pages (défaut: 50)")
    parser.add_argument("--apikey", "-k", required=True,            help="Clé API ScraperAPI")
    parser.add_argument("--outdir", "-o", default="html_dump",      help="Dossier de sortie (défaut: html_dump)")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    print(f"\n🚀 Dump HTML — '{args.query}' — {args.pages} pages → ./{args.outdir}/\n")

    ok, fail = 0, 0
    for page_num in range(1, args.pages + 1):
        url = f"{BASE_URL}/s?k={args.query.replace(' ', '+')}&page={page_num}&language=fr_FR"
        print(f"[{page_num:02d}/{args.pages}] {url} ... ", end="", flush=True)

        html = fetch(url, args.apikey)

        if not html:
            print("❌ vide")
            fail += 1
            continue

        filename = os.path.join(args.outdir, f"page_{page_num:02d}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ {len(html):,} chars → {filename}")
        ok += 1
        time.sleep(random.uniform(0.5, 1.5))

    print(f"\n{'='*50}")
    print(f"✅ {ok} pages sauvegardées | ❌ {fail} échecs")
    print(f"📁 Dossier : ./{args.outdir}/")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()