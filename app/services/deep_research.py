import httpx
import json
import re

from app.config import settings


class DeepResearchError(Exception):
    """Custom exception for deep research errors"""
    pass


def extract_json(text: str) -> str:
    """Extract JSON from text that may contain markdown code blocks or extra content"""
    text = re.sub(r'```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```', '', text.strip())

    # Find the first opening brace
    start = text.find('{')
    if start == -1:
        return text

    # Track brace depth to find matching closing brace
    depth = 0
    in_string = False
    escape_next = False
    end = start

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if depth == 0 and end > start:
        return text[start:end + 1]

    return text


class DeepResearchService:
    def __init__(self):
        self.api_key = settings.deep_agent_key
        self.api_url = settings.deep_endpoint
        self.timeout = 120.0  # Longer timeout for deep research

    async def question_analyze(self, ticker: str) -> dict:
        """
        Send a stock ticker to get analysis content.
        Extracts and returns parsed JSON from the response.
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
                raise DeepResearchError(f"API returned status {response.status_code}")

            data = response.json()

        # Extract and parse JSON from the response
        try:
            content = data["choices"][0]["message"]["content"]
            clean_json = extract_json(content)
            try:
                return json.loads(clean_json)
            except json.JSONDecodeError:
                # If JSON parsing fails, return raw content with error info
                return {"raw_content": content, "parse_error": "Could not extract valid JSON from response"}
        except KeyError as e:
            raise DeepResearchError(f"Invalid response structure: {e}")

    async def deep_analyze(self, ticker: str) -> dict:
        """
        Send a stock ticker to the Deep Research agent for comprehensive analysis.
        Returns the parsed response.
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
                raise DeepResearchError(f"API returned status {response.status_code}")

            data = response.json()

        return self._parse_response(data)

    def _parse_response(self, data: dict) -> dict:
        """Parse the raw API response"""
        try:
            content = data["choices"][0]["message"]["content"]
            # Try to parse as JSON first
            clean_json = extract_json(content)
            try:
                return json.loads(clean_json)
            except json.JSONDecodeError:
                # If not valid JSON, return as text content
                return {"content": content, "format": "text"}
        except KeyError as e:
            raise DeepResearchError(f"Invalid response structure: {e}")
        except Exception as e:
            raise DeepResearchError(f"Error parsing response: {e}")


# Singleton instance
deep_research_service = DeepResearchService()
