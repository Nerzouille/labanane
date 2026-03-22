"""Feature 002 workflow pipeline entity models."""

from typing import Literal
from pydantic import BaseModel

from .report import (
    Product as MarketplaceProduct,  # backwards-compat alias
    TargetPersona,
    DifferentiationAngles,
    CompetitiveOverview,
)


class KeywordSet(BaseModel):
    keywords: list[str]  # 3-5 items
    source_description: str


class ProductBatch(BaseModel):
    products: list[MarketplaceProduct]  # length >= 1
    source_keywords: list[str]


class MarketData(BaseModel):
    products: list[MarketplaceProduct]
    trend_data: dict | None = None
    sentiment_data: dict | None = None
    sources_available: list[str] = []
    sources_unavailable: list[str] = []


class AnalysisResult(BaseModel):
    target_persona: TargetPersona | None = None
    differentiation_angles: DifferentiationAngles | None = None
    competitive_overview: CompetitiveOverview | None = None


class FinalCriteria(BaseModel):
    summary: str
    go_no_go: Literal["go", "no-go", "conditional"]
    key_risks: list[str]       # 3-5 items
    key_opportunities: list[str]  # 3-5 items


class Report(BaseModel):
    run_id: str
    keyword: str
    analysis: AnalysisResult | None = None
    final_criteria: FinalCriteria | None = None
    products: list[MarketplaceProduct] = []
    markdown: str | None = None
