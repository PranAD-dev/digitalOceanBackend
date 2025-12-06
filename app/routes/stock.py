from fastapi import APIRouter, HTTPException, Query

from app.models import StockAnalysisResponse
from app.services.stock_agent import stock_agent_service, StockAgentError

router = APIRouter(prefix="/api/v1/stock", tags=["Stock Analysis"])


@router.get("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., NVDA, AAPL)", min_length=1, max_length=10)
):
    """
    Analyze a stock using AI-powered due diligence.

    Returns comprehensive analysis including:
    - Current price and verdict (BUY/SELL/NEUTRAL)
    - Confidence score (0-100)
    - Executive summary
    - Fundamental analysis
    - Upcoming catalysts
    - Red flags to watch
    """
    try:
        result = await stock_agent_service.analyze_stock(ticker)
        return result
    except StockAgentError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/quick/{ticker}")
async def quick_analysis(ticker: str):
    """
    Quick analysis endpoint - returns just the verdict and confidence.
    Useful for dashboard widgets or quick checks.
    """
    try:
        result = await stock_agent_service.analyze_stock(ticker)
        return {
            "ticker": result.ticker,
            "verdict": result.verdict,
            "confidence_score": result.confidence_score,
            "current_price": result.current_price
        }
    except StockAgentError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
