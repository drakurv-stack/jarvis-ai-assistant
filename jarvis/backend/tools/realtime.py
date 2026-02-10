"""
Realtime Tools - Web search and live information retrieval
"""
import asyncio
import os
from typing import Optional
import aiohttp
from urllib.parse import quote_plus


class RealtimeTools:
    """
    Handles realtime information retrieval including web search.
    Uses DuckDuckGo or SerpAPI depending on configuration.
    """

    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.timeout = aiohttp.ClientTimeout(total=10)

    async def web_search(self, query: str, num_results: int = 5) -> str:
        """
        Search the web for information.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Formatted search results
        """
        # Try SerpAPI first if key is available
        if self.serpapi_key:
            result = await self._serpapi_search(query, num_results)
            if result:
                return result

        # Fallback to DuckDuckGo
        result = await self._duckduckgo_search(query, num_results)
        if result:
            return result

        return "I couldn't find any search results. Please try a different query."

    async def _serpapi_search(self, query: str, num_results: int) -> Optional[str]:
        """Search using SerpAPI (Google results)"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "engine": "google"
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None

                    data = await response.json()

                    results = []

                    # Answer box if available
                    if "answer_box" in data:
                        box = data["answer_box"]
                        if "answer" in box:
                            results.append(f"Quick Answer: {box['answer']}")
                        elif "snippet" in box:
                            results.append(f"Quick Answer: {box['snippet']}")

                    # Organic results
                    organic = data.get("organic_results", [])
                    for i, item in enumerate(organic[:num_results], 1):
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        results.append(f"{i}. {title}\n   {snippet}")

                    return "\n\n".join(results) if results else None

        except Exception as e:
            print(f"SerpAPI error: {e}")
            return None

    async def _duckduckgo_search(self, query: str, num_results: int) -> Optional[str]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return await self._duckduckgo_html_search(query, num_results)

                    data = await response.json()

                    results = []

                    # Abstract (main answer)
                    if data.get("Abstract"):
                        results.append(f"Summary: {data['Abstract']}")

                    # Related topics
                    for topic in data.get("RelatedTopics", [])[:num_results]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results.append(topic["Text"])

                    if results:
                        return "\n\n".join(results)

                    # If no instant answer, try HTML scraping fallback
                    return await self._duckduckgo_html_search(query, num_results)

        except Exception as e:
            print(f"DuckDuckGo API error: {e}")
            return await self._duckduckgo_html_search(query, num_results)

    async def _duckduckgo_html_search(self, query: str, num_results: int) -> Optional[str]:
        """Fallback: Scrape DuckDuckGo HTML results"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()

                    # Simple parsing without BeautifulSoup
                    results = []
                    import re

                    # Extract result snippets
                    snippets = re.findall(
                        r'class="result__snippet"[^>]*>(.*?)</a>',
                        html,
                        re.DOTALL
                    )

                    for i, snippet in enumerate(snippets[:num_results], 1):
                        # Clean HTML tags
                        clean = re.sub(r'<[^>]+>', '', snippet).strip()
                        if clean:
                            results.append(f"{i}. {clean}")

                    return "\n\n".join(results) if results else None

        except Exception as e:
            print(f"DuckDuckGo HTML search error: {e}")
            return None

    async def get_weather(self, location: str) -> str:
        """
        Get weather information (placeholder - requires API key)
        """
        # This would require a weather API key (OpenWeatherMap, WeatherAPI, etc.)
        return f"Weather functionality requires a weather API key. You asked about weather in {location}."
