import uuid
import asyncio
import json
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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
    
    # TODO: Call OpenHosta to generate 3 search queries
    mock_queries = [
        f"{request.product_description} cheap",
        f"{request.product_description} reviews",
        f"buy {request.product_description} online"
    ]
    
    MEMORY_STORE[session_id]["search_queries"] = mock_queries
    
    return InitSearchResponse(
        session_id=session_id,
        search_queries=mock_queries
    )

@app.post("/api/scrape-stream/{session_id}")
async def scrape_stream(session_id: str, request: ScrapeStreamRequest):
    if session_id not in MEMORY_STORE:
        raise HTTPException(status_code=404, detail="Invalid or expired session")
        
    MEMORY_STORE[session_id]["search_queries"] = request.final_queries
    
    sources = ["Amazon", "Google Shopping", "Reddit"]
    for source in sources:
        MEMORY_STORE[session_id]["products_by_source"][source] = []

    async def event_generator():
        # TODO: Launch asynchronous scrapers in parallel
        # Use asyncio.as_completed to yield results as soon as a source finishes
        
        for source in sources:
            await asyncio.sleep(2) # Mock scraping delay
            
            mock_products = [
                {"title": f"Mock Product 1 from {source}", "price": "19.99", "url": "https://..."},
                {"title": f"Mock Product 2 from {source}", "price": "29.99", "url": "https://..."}
            ]
            
            MEMORY_STORE[session_id]["products_by_source"][source].extend(mock_products)
            
            yield f"event: source_ready\n"
            yield f"data: {json.dumps({'source': source, 'products': mock_products})}\n\n"
            
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
