"""
Brain Router - Decision Making Model
Classifies user requests into GENERAL_QUERY, REALTIME_QUERY, or AUTOMATION_QUERY
"""
import re
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.schemas import QueryType, BrainDecision


class BrainRouter:
    """
    Routes user queries to the appropriate handler based on intent classification.
    Uses keyword matching and pattern recognition for MVP.
    Can be upgraded to use an LLM classifier later.
    """

    def __init__(self):
        # Automation patterns and their intents
        self.automation_patterns = {
            # Website opening
            r"open\s+(?:the\s+)?(?:website\s+)?(\S+\.(?:com|org|net|io|co|edu|gov|ai))\b": ("open_website", "url"),
            r"go\s+to\s+(\S+\.(?:com|org|net|io|co|edu|gov|ai))\b": ("open_website", "url"),
            r"open\s+(?:the\s+)?(?:website\s+)?(youtube|google|gmail|twitter|facebook|reddit|github|netflix|spotify)": ("open_website", "site_name"),

            # App opening
            r"open\s+(?:the\s+)?(?:app\s+|application\s+)?(?:called\s+)?(notepad|calculator|chrome|firefox|edge|word|excel|powerpoint|outlook|terminal|cmd|vscode|code|spotify|discord|slack|teams|zoom)": ("open_app", "app_name"),
            r"launch\s+(?:the\s+)?(?:app\s+|application\s+)?(?:called\s+)?(\w+)": ("open_app", "app_name"),
            r"start\s+(?:the\s+)?(?:app\s+|application\s+)?(?:called\s+)?(\w+)": ("open_app", "app_name"),

            # Reminders
            r"remind\s+me\s+(?:to\s+)?(.+?)\s+in\s+(\d+)\s*(?:minute|min|minutes|mins)": ("set_reminder", "reminder_with_time"),
            r"set\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+?)\s+in\s+(\d+)\s*(?:minute|min|minutes|mins)": ("set_reminder", "reminder_with_time"),
            r"remind\s+me\s+(?:to\s+)?(.+)": ("set_reminder", "reminder_text"),

            # Notes
            r"(?:take\s+(?:a\s+)?note|write\s+(?:a\s+)?note|note\s+(?:down|this)|jot\s+(?:down|this))[\s:]+(.+)": ("take_note", "note_text"),
            r"save\s+(?:this\s+)?(?:as\s+)?(?:a\s+)?note[\s:]+(.+)": ("take_note", "note_text"),

            # System commands
            r"(?:what(?:'s|\s+is)\s+the\s+)?(?:current\s+)?time\??": ("get_time", None),
            r"(?:what(?:'s|\s+is)\s+)?(?:today(?:'s|\s+)?)?date\??": ("get_date", None),
        }

        # Realtime query indicators
        self.realtime_keywords = [
            "search", "look up", "find out", "google",
            "what is the latest", "what's the latest",
            "current news", "recent news", "today's news",
            "weather", "forecast",
            "stock price", "stocks",
            "how much is", "price of",
            "who won", "score", "results",
            "breaking", "happening now",
            "trending", "viral",
            "release date", "when is",
            "reviews of", "rating of"
        ]

        # Site name to URL mapping
        self.site_urls = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "gmail": "https://gmail.com",
            "twitter": "https://twitter.com",
            "facebook": "https://facebook.com",
            "reddit": "https://reddit.com",
            "github": "https://github.com",
            "netflix": "https://netflix.com",
            "spotify": "https://spotify.com"
        }

    async def route(self, query: str) -> BrainDecision:
        """
        Analyze the query and return a routing decision.
        """
        query_lower = query.lower().strip()

        # Check for automation patterns first
        for pattern, (intent, param_type) in self.automation_patterns.items():
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                parameters = self._extract_parameters(match, intent, param_type, query_lower)
                return BrainDecision(
                    query_type=QueryType.AUTOMATION_QUERY,
                    intent=intent,
                    parameters=parameters,
                    confidence=0.9
                )

        # Check for realtime query indicators
        for keyword in self.realtime_keywords:
            if keyword in query_lower:
                return BrainDecision(
                    query_type=QueryType.REALTIME_QUERY,
                    intent="web_search",
                    parameters={"query": query},
                    confidence=0.8
                )

        # Default to general query
        return BrainDecision(
            query_type=QueryType.GENERAL_QUERY,
            intent="chat",
            parameters={"query": query},
            confidence=0.7
        )

    def _extract_parameters(self, match, intent: str, param_type: str, query: str) -> dict:
        """Extract parameters from regex match"""
        params = {}

        if intent == "open_website":
            if param_type == "site_name":
                site = match.group(1).lower()
                params["url"] = self.site_urls.get(site, f"https://{site}.com")
            else:
                url = match.group(1)
                if not url.startswith("http"):
                    url = f"https://{url}"
                params["url"] = url

        elif intent == "open_app":
            params["app_name"] = match.group(1).lower()

        elif intent == "set_reminder":
            if param_type == "reminder_with_time":
                params["text"] = match.group(1)
                params["time_minutes"] = int(match.group(2))
            else:
                params["text"] = match.group(1)
                params["time_minutes"] = 5  # Default 5 minutes

        elif intent == "take_note":
            params["text"] = match.group(1)

        return params
