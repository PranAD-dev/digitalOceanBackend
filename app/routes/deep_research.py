from fastapi import APIRouter, HTTPException

from app.services.deep_research import deep_research_service, DeepResearchError

router = APIRouter(prefix="/api/v1/research", tags=["Deep Research"])


@router.get("/deep/{ticker}")
async def deep_research(ticker: str):
    """
    Perform deep research analysis on a stock.

    This endpoint uses a more comprehensive AI agent that performs
    in-depth analysis on the given stock ticker.

    Note: This endpoint may take longer to respond due to the depth of analysis.
    """
    try:
        result = await deep_research_service.deep_analyze(ticker)
        return result
    except DeepResearchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/question/{ticker}")
async def question_research(ticker: str):
    """
    Get analysis content for a stock ticker.
    Returns parsed JSON from the questioning agent response.
    """
    try:
        result = await deep_research_service.question_analyze(ticker)
        return result
    except DeepResearchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
