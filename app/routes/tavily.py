from fastapi import APIRouter, HTTPException

from app.services.deep_research import deep_research_service, DeepResearchError
from app.services.tavily_search import tavily_search_service, TavilySearchError

router = APIRouter(prefix="/api/v1/search", tags=["Tavily Search"])


@router.get("/tavily/{ticker}")
async def tavily_research(ticker: str):
    try:
        deep_result = await deep_research_service.deep_analyze(ticker.upper())

        questions = []
        if isinstance(deep_result, dict):
            for key in ["questions", "research_questions", "follow_up_questions", "queries"]:
                if key in deep_result and isinstance(deep_result[key], list):
                    questions = deep_result[key]
                    break

            if not questions:
                for value in deep_result.values():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
                        questions = value
                        break

        if not questions and "content" in deep_result:
            content = deep_result.get("content", "")
            lines = content.split("\n")
            questions = [line.strip() for line in lines if line.strip().endswith("?")][:7]

        if not questions:
            return {
                "ticker": ticker.upper(),
                "error": "No questions found from deep research",
                "deep_research_response": deep_result
            }

        selected_questions = questions[:3]

        answers = await tavily_search_service.search_multiple(
            questions=selected_questions,
            topic="finance"
        )

        return {
            "ticker": ticker.upper(),
            "questions_found": len(questions),
            "questions_searched": len(selected_questions),
            "results": answers
        }

    except DeepResearchError as e:
        raise HTTPException(status_code=502, detail=f"Deep research error: {str(e)}")
    except TavilySearchError as e:
        raise HTTPException(status_code=502, detail=f"Tavily search error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
