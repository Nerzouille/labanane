"""Shared domain models for workflow steps."""

from pydantic import BaseModel


class MarketplaceProduct(BaseModel):
    title: str
    price: str  # formatted string, e.g. "$14.99" or "N/A"
    url: str


class ViabilityScore(BaseModel):
    score: int  # 0-100
    explanation: str


class TargetPersona(BaseModel):
    description: str


class DifferentiationAngles(BaseModel):
    content: str


class CompetitiveOverview(BaseModel):
    content: str


class SourceResult(BaseModel):
    source: str
    status: str  # "success" | "timeout" | "error"
    data: dict | None = None
    error_message: str | None = None
