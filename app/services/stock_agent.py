import httpx
import json
import re

from app.config import settings
from app.models.stock import StockAnalysisResponse


class StockAgentError(Exception):
    pass


def fix_json(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())

    start = text.find('{')
    end = text.rfind('}')

    if start != -1 and end != -1:
        text = text[start:end + 1]

    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    return text


def safe_parse(parsed: dict) -> dict:
    defaults = {
        "ticker": parsed.get("ticker", "UNKNOWN"),
        "current_price": parsed.get("current_price"),
        "verdict": parsed.get("verdict", "NEUTRAL"),
        "confidence_score": min(max(int(parsed.get("confidence_score", 50)), 0), 100),
        "executive_summary": parsed.get("executive_summary", "Analysis unavailable."),
        "fundamentals": parsed.get("fundamentals", {
            "valuation_rating": "FAIR",
            "health_check": "Data unavailable."
        }),
        "catalysts": parsed.get("catalysts", []),
        "red_flags": parsed.get("red_flags", [])
    }

    if isinstance(defaults["fundamentals"], dict):
        defaults["fundamentals"]["valuation_rating"] = defaults["fundamentals"].get("valuation_rating", "FAIR")
        defaults["fundamentals"]["health_check"] = defaults["fundamentals"].get("health_check", "Data unavailable.")

    valid_verdicts = ["BUY", "SELL", "NEUTRAL"]
    if defaults["verdict"] not in valid_verdicts:
        defaults["verdict"] = "NEUTRAL"

    valid_ratings = ["OVERVALUED", "UNDERVALUED", "FAIR"]
    if defaults["fundamentals"].get("valuation_rating") not in valid_ratings:
        defaults["fundamentals"]["valuation_rating"] = "FAIR"

    return defaults


class StockAgentService:
    def __init__(self):
        self.api_key = settings.stock_agent_key
        self.api_url = settings.agent_endpoint
        self.timeout = 90.0

    async def analyze_stock(self, ticker: str) -> StockAnalysisResponse:
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

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    raise StockAgentError(f"API returned status {response.status_code}")

                data = response.json()
        except httpx.TimeoutException:
            raise StockAgentError("Request timed out")
        except httpx.RequestError as e:
            raise StockAgentError(f"Request failed: {e}")

        return self._parse_response(data, ticker)

    def _parse_response(self, data: dict, ticker: str) -> StockAnalysisResponse:
        try:
            content = data["choices"][0]["message"]["content"]
            clean_json = fix_json(content)
            parsed = json.loads(clean_json)
            safe_data = safe_parse(parsed)
            safe_data["ticker"] = ticker.upper()
            return StockAnalysisResponse(**safe_data)
        except (KeyError, json.JSONDecodeError, TypeError) as e:
            raise StockAgentError(f"Failed to parse response: {e}")


stock_agent_service = StockAgentService()
