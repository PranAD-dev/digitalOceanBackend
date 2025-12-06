import httpx
import json
import re

from app.config import settings
from app.models.stock import StockAnalysisResponse


class StockAgentError(Exception):
    """Custom exception for stock agent errors"""
    pass


def extract_json(text: str) -> str:
    """Extract JSON from text that may contain markdown code blocks or extra content"""
    # Remove markdown code blocks if present
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())

    # Find JSON object boundaries
    start = text.find('{')
    end = text.rfind('}')

    if start != -1 and end != -1:
        return text[start:end + 1]

    return text


class StockAgentService:
    def __init__(self):
        self.api_key = settings.stock_agent_key
        self.api_url = settings.agent_endpoint
        self.timeout = 60.0

    async def analyze_stock(self, ticker: str) -> StockAnalysisResponse:
        """
        Send a stock ticker to the DigitalOcean GenAI agent for analysis.
        Returns a parsed StockAnalysisResponse.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": ticker.upper()
                }
            ],
            "stream": False,
            "include_functions_info": True,
            "include_retrieval_info": True,
            "include_guardrails_info": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/api/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                raise StockAgentError(f"API returned status {response.status_code}")

            data = response.json()

        return self._parse_response(data)

    def _parse_response(self, data: dict) -> StockAnalysisResponse:
        """Parse the raw API response into a StockAnalysisResponse"""
        try:
            content = data["choices"][0]["message"]["content"]
            # Clean up the content to extract valid JSON
            clean_json = extract_json(content)
            parsed = json.loads(clean_json)
            return StockAnalysisResponse(**parsed)
        except KeyError as e:
            raise StockAgentError(f"Invalid response structure: {e}")
        except json.JSONDecodeError as e:
            raise StockAgentError(f"Failed to parse JSON content: {e}")
        except Exception as e:
            raise StockAgentError(f"Error parsing response: {e}")


# Singleton instance
stock_agent_service = StockAgentService()
