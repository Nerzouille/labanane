from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Any

# --- Analysis Schemas ---

class AnalysisBase(BaseModel):
    market_bilan: str
    persona: Dict[str, Any]
    strategy: str

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: int
    search_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Product Schemas ---

class ProductBase(BaseModel):
    source: str
    title: str
    price: str
    features: List[str]
    url: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    search_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Search Schemas ---

class SearchBase(BaseModel):
    user_query: str

class SearchCreate(SearchBase):
    pass

class SearchResponse(SearchBase):
    id: int
    created_at: datetime
    products: List[ProductResponse] = []
    analyses: List[AnalysisResponse] = []

    model_config = ConfigDict(from_attributes=True)
