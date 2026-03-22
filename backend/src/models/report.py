"""Shared domain models for workflow steps."""
from typing import Literal
from pydantic import BaseModel, Field


class Product(BaseModel):
    title: str
    price: str           # formatted, e.g. "EUR 14.99" or "N/A"
    url: str             # absolute product URL
    rating_stars: float  # 0.0–5.0
    rating_range: int    # max rating value, typically 5
    rating_count: int    # total review count
    main_features: list[str] = Field(min_length=3, max_length=3)


class TargetPersona(BaseModel):
    description: str


class DifferentiationAngles(BaseModel):
    content: str


class CompetitiveOverview(BaseModel):
    content: str


class Criterion(BaseModel):
    label: str   # e.g. "Market size"
    score: int   # 0–100


class MarketAnalysis(BaseModel):
    viability_score: int                                    # 0–100
    go_no_go: Literal["go", "no-go", "conditional"]
    summary: str                                            # 1-sentence verdict
    analysis: str                                           # 2–3 sentence analysis
    key_risks: list[str]                                    # top 3
    key_opportunities: list[str]                            # top 3
    criteria: list[Criterion]                               # 3–5 scoring dimensions
    target_persona: TargetPersona
    differentiation_angles: DifferentiationAngles
    competitive_overview: CompetitiveOverview


class SourceResult(BaseModel):
    source: str
    status: str  # "success" | "timeout" | "error"
    data: dict | None = None
    error_message: str | None = None
