import os
import json
import subprocess
import sys
from dotenv import load_dotenv
from .cache import SemanticCache
from .metrics import SavingsTracker

load_dotenv()

def _call_gemini_subprocess(prompt: str, api_key: str) -> str:
    """
    Run the Gemini API call in a completely separate Python process
    so it never conflicts with torch in the main process.
    """
    code = f"""
import os
os.environ['GEMINI_API_KEY'] = {repr(api_key)}
from google import genai
client = genai.Client(api_key={repr(api_key)})
result = client.models.generate_content(model='gemini-2.0-flash', contents={repr(prompt)})
print(result.text)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"Gemini call failed: {result.stderr[:300]}")
    return result.stdout.strip()


class EcoCacheClient:
    def __init__(self, api_key: str = None, similarity_threshold: float = 0.85):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key found. Set GEMINI_API_KEY in your .env file.")

        self.cache = SemanticCache(similarity_threshold=similarity_threshold)
        self.tracker = SavingsTracker()

    def chat(self, prompt: str, **kwargs) -> dict:
        # 1. Check cache first
        cached_response, similarity = self.cache.get(prompt)

        if cached_response:
            self.tracker.record(prompt, was_cached=True, similarity=similarity)
            return {
                "response": cached_response,
                "source": "cache",
                "similarity": round(similarity, 3),
                "savings": self.tracker.summary()
            }

        # 2. Cache miss — call Gemini in a subprocess (avoids torch conflict)
        print("Cache miss — calling Gemini API...")
        response_text = _call_gemini_subprocess(prompt, self.api_key)

        # 3. Store for future similar queries
        self.cache.store(prompt, response_text)
        self.tracker.record(prompt, was_cached=False, similarity=similarity)

        return {
            "response": response_text,
            "source": "api",
            "similarity": round(similarity, 3),
            "savings": self.tracker.summary()
        }

    def summary(self):
        self.tracker.print_summary()