import httpx
import json

from app.config import settings


class DeepResearchError(Exception):
    """Custom exception for deep research errors"""
    pass


async def extract_json_with_claude(text: str) -> dict:
    """Use Claude API to extract and format JSON from unstructured text"""
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 8192,
        "messages": [
            {
                "role": "user",
                "content": f"""Extract the JSON object from the following text and return ONLY the valid JSON, nothing else.
Do not include any markdown code blocks, explanations, or extra text. Just the raw JSON object.

Text:
{text}"""
            }
        ]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise DeepResearchError(f"Claude API error: {response.status_code} - {response.text}")
        print("/n/n/n/n")
        print(response.content)
        print("/n/n/n/n")
        result = response.json()
        content = result.get("content", [{}])[0].get("text", "")

        # Strip markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()

        # Parse the cleaned JSON
        return json.loads(content)


class DeepResearchService:
    def __init__(self):
        self.api_key = settings.deep_agent_key
        self.api_url = settings.deep_endpoint
        # Use granular timeouts for streaming: longer read timeout for slow responses
        self.timeout = httpx.Timeout(
            connect=30.0,    # Time to establish connection
            read=300.0,      # Time to wait for data (5 min for slow AI responses)
            write=30.0,      # Time to send request
            pool=30.0        # Time to acquire connection from pool
        )

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
            "stream": True,
            "include_functions_info": False,
            "include_retrieval_info": False,
            "include_guardrails_info": False
        }

        full_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.api_url}/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    await response.aread()
                    raise DeepResearchError(f"API returned status {response.status_code}: {response.text}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            full_content += delta["content"]
        # Use Claude to extract and format JSON from the response
        try:
            return await extract_json_with_claude(full_content)
        except json.JSONDecodeError as e:
            raise DeepResearchError(f"Failed to parse JSON from response: {e}")

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
            "stream": True,
            "include_functions_info": False,
            "include_retrieval_info": False,
            "include_guardrails_info": False
        }

        full_content = ""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.api_url}/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status_code != 200:
                    await response.aread()
                    raise DeepResearchError(f"API returned status {response.status_code}: {response.text}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            full_content += delta["content"]
        print(full_content)
        # Use Claude to extract and format JSON from the response
        try:
            return await extract_json_with_claude(full_content)
        except json.JSONDecodeError as e:
            raise DeepResearchError(f"Failed to parse JSON from response: {e}")


# Singleton instance
deep_research_service = DeepResearchService()
