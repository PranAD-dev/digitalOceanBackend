from fastapi import APIRouter, HTTPException, Query

from app.services.deep_research import deep_research_service, DeepResearchError

router = APIRouter(prefix="/api/v1/research", tags=["Deep Research"])


@router.get("/deep")
async def deep_research(
    query: str = Query(..., description="Stock ticker or follow-up question for deep research")
):
    """
    Perform deep research analysis on a stock.

    This endpoint uses a more comprehensive AI agent that performs
    in-depth analysis. It can accept:
    - A stock ticker (e.g., "NVDA") for initial research
    - Follow-up questions to continue the research conversation

    Note: This endpoint may take longer to respond due to the depth of analysis.
    """
    try:
        result = await deep_research_service.deep_analyze(query)
        return result
    except DeepResearchError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
