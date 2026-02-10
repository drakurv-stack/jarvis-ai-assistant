"""
Chat Service - Handles LLM conversations
Uses OpenAI-compatible API or local models
"""
import os
import asyncio
from typing import Optional, List, Dict


class ChatService:
    """
    Chat service for general conversation and summarization.
    Supports OpenAI API or can be adapted for local models.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
        self.conversation_history: List[Dict] = []
        self.max_history = 10  # Keep last 10 exchanges

        # System prompt for JARVIS personality
        self.system_prompt = """You are J.A.R.V.I.S., an advanced AI assistant inspired by Tony Stark's AI.
You are helpful, intelligent, witty, and occasionally sarcastic but always respectful.
Keep responses concise and natural - suitable for voice output.
You assist with information, tasks, and conversation.
When you don't know something, admit it clearly.
Respond in a friendly, conversational tone."""

        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize the OpenAI client if API key is available"""
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
                print(f"✅ Chat service initialized with model: {self.model}")
            except ImportError:
                print("⚠️ openai package not installed")
                self._client = None
        else:
            print("⚠️ No OPENAI_API_KEY found - using fallback responses")

    async def get_response(self, user_message: str) -> str:
        """
        Get a response for a user message.

        Args:
            user_message: The user's input

        Returns:
            AI response text
        """
        if not self._client:
            return self._fallback_response(user_message)

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Trim history if needed
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-(self.max_history * 2):]

        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)

            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )

            assistant_message = response.choices[0].message.content

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            print(f"❌ Chat API error: {e}")
            return self._fallback_response(user_message)

    async def summarize_search(self, query: str, search_results: str) -> str:
        """
        Summarize search results for the user.

        Args:
            query: Original user query
            search_results: Raw search results text

        Returns:
            Summarized response
        """
        if not self._client:
            # Return raw results if no LLM available
            return f"Here's what I found: {search_results[:500]}..."

        prompt = f"""Based on the following search results, provide a concise answer to the user's question.
Be direct and informative. If the search results don't contain relevant information, say so.

User Question: {query}

Search Results:
{search_results[:3000]}

Provide a helpful, concise response:"""

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes search results clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.5
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return f"I found some information but couldn't summarize it properly. Here's what I found: {search_results[:300]}..."

    def _fallback_response(self, message: str) -> str:
        """Provide fallback responses when no LLM is available"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm JARVIS. I'm running in limited mode without an AI backend. Set your OPENAI_API_KEY to enable full capabilities."

        if "how are you" in message_lower:
            return "I'm functioning within normal parameters, though I'm currently operating in limited mode."

        if any(word in message_lower for word in ["thank", "thanks"]):
            return "You're welcome! Happy to help."

        if "?" in message:
            return "I apologize, but I'm running in limited mode without an AI backend. Please set your OPENAI_API_KEY environment variable to enable full conversational capabilities."

        return "I understood your message, but I'm currently running in limited mode. Please configure an API key for full functionality."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
