import os
from openai import OpenAI
from dotenv import load_dotenv
from .cache import SemanticCache
from .metrics import SavingsTracker

load_dotenv()

class EcoCacheClient:
    def __init__(self, api_key: str = None, similarity_threshold: float = 0.85):
        # Use passed key or fall back to .env file
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("No API key found. Pass one in or set OPENAI_API_KEY in your .env file.")

        self.llm = OpenAI(api_key=key)
        self.cache = SemanticCache(similarity_threshold=similarity_threshold)
        self.tracker = SavingsTracker()

    def chat(self, prompt: str, model: str = "gpt-3.5-turbo") -> dict:
        """
        Drop-in replacement for a normal LLM call.
        Checks cache first — only calls the API on a miss.

        Returns a dict with:
          - response: the answer text
          - source: 'cache' or 'api'
          - similarity: how close the match was (0-1)
          - savings: running totals of water/carbon saved
        """

        # 1. Check the cache first
        cached_response, similarity = self.cache.get(prompt)

        if cached_response:
            # Cache hit — return instantly, no API call
            self.tracker.record(prompt, was_cached=True, similarity=similarity)
            return {
                "response": cached_response,
                "source": "cache",
                "similarity": round(similarity, 3),
                "savings": self.tracker.summary()
            }

        # 2. Cache miss — call the real API
        print("Calling LLM API...")
        completion = self.llm.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = completion.choices[0].message.content

        # 3. Store this new response so future similar queries hit cache
        self.cache.store(prompt, response_text)
        self.tracker.record(prompt, was_cached=False, similarity=similarity)

        return {
            "response": response_text,
            "source": "api",
            "similarity": round(similarity, 3),
            "savings": self.tracker.summary()
        }

    def summary(self):
        """Print a summary of savings so far."""
        self.tracker.print_summary()