from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Verdict(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class ValuationRating(str, Enum):
    OVERVALUED = "OVERVALUED"
    UNDERVALUED = "UNDERVALUED"
    FAIR = "FAIR"


class CatalystImpact(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class StockAnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA, AAPL)")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "NVDA"
            }
        }


class Fundamentals(BaseModel):
    valuation_rating: ValuationRating
    health_check: str


class Catalyst(BaseModel):
    event: str
    impact: CatalystImpact
    description: str


class StockAnalysisResponse(BaseModel):
    ticker: str
    current_price: Optional[float] = None
    verdict: Verdict
    confidence_score: int = Field(..., ge=0, le=100)
    executive_summary: str
    fundamentals: Fundamentals
    catalysts: list[Catalyst] = []
    red_flags: list[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "NVDA",
                "current_price": 620.45,
                "verdict": "NEUTRAL",
                "confidence_score": 72,
                "executive_summary": "Nvidia remains a dominant player in AI compute...",
                "fundamentals": {
                    "valuation_rating": "OVERVALUED",
                    "health_check": "Robust balance sheet with $28B cash..."
                },
                "catalysts": [
                    {
                        "event": "Q3 FY2025 Earnings Release",
                        "impact": "POSITIVE",
                        "description": "Expect continuation of double-digit revenue growth..."
                    }
                ],
                "red_flags": [
                    "P/E ratio above 70x forward earnings"
                ]
            }
        }


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    service: str
