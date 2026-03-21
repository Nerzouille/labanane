import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("TestClient")

BASE_URL = "http://localhost:8000"

async def test_workflow():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # --- ETAPE 1 : Initialisation de la recherche ---
        logger.info("=== 1. Init Search ===")
        try:
            init_resp = await client.post(f"{BASE_URL}/api/init-search", json={
                "product_description": "t-shirt rouge avec un chat"
            })
            init_resp.raise_for_status()
        except httpx.ConnectError:
            logger.error(f"❌ Impossible de se connecter à {BASE_URL}. Le serveur FastAPI tourne-t-il ?")
            return
            
        init_data = init_resp.json()
        session_id = init_data["session_id"]
        queries = init_data["search_queries"]
        logger.info(f"✅ Session ID généré : {session_id}")
        logger.info(f"✅ Mots-clés IA : {queries}\n")
        
        # --- ETAPE 2 : Scraping & Streaming Asynchrone ---
        logger.info("=== 2. Scrape Stream (SSE) ===")
        async with client.stream("POST", f"{BASE_URL}/api/scrape-stream/{session_id}", json={
            "final_queries": queries
        }, timeout=None) as stream_resp:  # On enlève la limite de temps pour le scrapping
            stream_resp.raise_for_status()
            
            # Lecture du flux Server-Sent Events ligne par ligne
            async for line in stream_resp.aiter_lines():
                if line.startswith("event: "):
                    event_name = line[len("event: "):].strip()
                    logger.info(f"📩 [Event SSE reçu] : {event_name}")
                elif line.startswith("data: "):
                    data_payload = line[len("data: "):].strip()
                    if data_payload and data_payload != "{}":
                        parsed = json.loads(data_payload)
                        source_name = parsed['source']
                        products = parsed['products']
                        logger.info(f"   ► {source_name} a fini ses requêtes ! {len(products)} produits extraits (dé-dupliqués).")
                        if products:
                            # Montrer le premier produit en exemple
                            p = products[0]
                            logger.info(f"      Exemple: {p.get('title')} | {p.get('price')} | {p.get('url')}\n")

        # --- ETAPE 3 : Stratégie & Bilan ---
        logger.info("\n=== 3. Generation Bilan ===")
        final_resp = await client.post(f"{BASE_URL}/api/generate-strategy/{session_id}")
        final_resp.raise_for_status()
        final_data = final_resp.json()
        logger.info(f"✅ Bilan généré : {final_data['market_bilan']}")
        logger.info(f"✅ Stratégie : {final_data['strategy']}")
        logger.info(f"✅ Persona : {final_data['persona']}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
