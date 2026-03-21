import uuid
import asyncio
import json
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.scraper import (
    fetch_html, 
    clean_html_for_llm, 
    parse_marketplace_data, 
    generate_search_queries
)

# --- 1. In-Memory Store ---
MEMORY_STORE: Dict[str, Dict[str, Any]] = {}

app = FastAPI(title="Market Intelligence In-Memory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Pydantic Schemas ---

class InitSearchRequest(BaseModel):
    product_description: str

class InitSearchResponse(BaseModel):
    session_id: str
    search_queries: List[str]

class ScrapeStreamRequest(BaseModel):
    final_queries: List[str]

class GenerateStrategyResponse(BaseModel):
    market_bilan: str
    persona: Dict[str, Any]
    strategy: str

# --- 3. Routes ---

@app.post("/api/init-search", response_model=InitSearchResponse)
async def init_search(request: InitSearchRequest):
    session_id = str(uuid.uuid4())
    
    MEMORY_STORE[session_id] = {
        "product_description": request.product_description,
        "search_queries": [],
        "products_by_source": {}
    }
    
    # Call OpenHosta to generate 3 search queries
    queries = await generate_search_queries(request.product_description)
    
    MEMORY_STORE[session_id]["search_queries"] = queries
    
    return InitSearchResponse(
        session_id=session_id,
        search_queries=queries
    )

async def process_single_source(source: str, queries: List[str]) -> dict:
    """Processes multiple queries for a single source, keeping only unique products (by URL)."""
    all_products = []
    seen_urls = set()
    
    for query in queries:
        raw_html = await fetch_html(source, query)
        clean_text = clean_html_for_llm(raw_html)
        
        # Uses OpenHosta to parse the cleaned marketplace page into structured data
        products_list = await parse_marketplace_data(clean_text)
        
        for p in products_list:
            key = p.get('url') or p.get('title')
            # Deduplication
            if key and key not in seen_urls:
                seen_urls.add(key)
                all_products.append(p)
                
    return {"source": source, "products": all_products}

@app.post("/api/scrape-stream/{session_id}")
async def scrape_stream(session_id: str, request: ScrapeStreamRequest):
    if session_id not in MEMORY_STORE:
        raise HTTPException(status_code=404, detail="Invalid or expired session")
        
    MEMORY_STORE[session_id]["search_queries"] = request.final_queries
    final_queries = request.final_queries
    
    sources = ["Amazon", "Google Shopping", "Reddit"]
    for source in sources:
        MEMORY_STORE[session_id]["products_by_source"][source] = []

    async def event_generator():
        # Create coroutines for each source
        tasks = [
            asyncio.create_task(process_single_source(source, final_queries))
            for source in sources
        ]
        
        # Yield results as soon as each source completes its set of queries
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                source_name = result["source"]
                products = result["products"]
                
                MEMORY_STORE[session_id]["products_by_source"][source_name] = products
                
                yield f"event: source_ready\n"
                yield f"data: {json.dumps(result)}\n\n"
            except Exception as e:
                # Basic error handling in stream
                yield f"event: error\n"
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        yield "event: stream_complete\n"
        yield "data: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/generate-strategy/{session_id}", response_model=GenerateStrategyResponse)
async def generate_strategy(session_id: str):
    if session_id not in MEMORY_STORE:
        raise HTTPException(status_code=404, detail="Invalid or expired session")
        
    session_data = MEMORY_STORE[session_id]
    all_products = session_data["products_by_source"]
    
    # TODO: Calculate average price, extract pain-points
    # TODO: Final LLM call to generate the market analysis
    
    mock_strategy = {
        "market_bilan": "High demand, but current products suffer from long delivery times.",
        "persona": {
            "name": "Julie, 28",
            "need": "Speed and guaranteed quality",
            "budget": "Comfortable"
        },
        "strategy": "Focus messaging on 24h delivery and source via short supply chains."
    }
    
    return GenerateStrategyResponse(**mock_strategy)
