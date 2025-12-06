import httpx
from typing import Optional

from app.config import settings


class TavilySearchError(Exception):
    """Custom exception for Tavily search errors"""
    pass


class TavilySearchService:
    def __init__(self):
        self.api_key = settings.tavily_api_key
        self.api_url = "https://api.tavily.com/search"
        self.timeout = 30.0

    async def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_answer: bool = True,
        include_raw_content: bool = False,
        topic: str = "finance"
    ) -> dict:
        """
        Search using Tavily API.

        Args:
            query: The search query (can be a question from deep research)
            search_depth: "basic" or "advanced"
            max_results: Number of results to return
            include_answer: Whether to include AI-generated answer
            include_raw_content: Whether to include raw page content
            topic: Topic category ("general", "finance", "news")
        """
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "topic": topic
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.api_url, json=payload)

            if response.status_code != 200:
                raise TavilySearchError(f"Tavily API returned status {response.status_code}: {response.text}")

            return response.json()

    async def search_multiple(self, questions: list[str], topic: str = "finance") -> list[dict]:
        """
        Search for multiple questions (useful for chaining with deep research).

        Args:
            questions: List of questions from deep research
            topic: Topic category

        Returns:
            List of search results for each question
        """
        results = []
        for question in questions:
            try:
                result = await self.search(query=question, topic=topic)
                results.append({
                    "question": question,
                    "answer": result.get("answer"),
                    "sources": [
                        {
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "snippet": r.get("content", "")[:500]
                        }
                        for r in result.get("results", [])
                    ]
                })
            except TavilySearchError as e:
                results.append({
                    "question": question,
                    "error": str(e)
                })
        return results


# Singleton instance
tavily_search_service = TavilySearchService()
