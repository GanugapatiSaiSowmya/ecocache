import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

def _call_gemini_http(prompt: str, api_key: str, model: str = "gemma-3-1b-it") -> str:
    """
    Call Gemini using plain urllib — no grpc, no subprocess, no torch conflict.
    Returns the generated text on success; raises RuntimeError on failure.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as he:
        body = he.read().decode("utf-8") if hasattr(he, "read") else ""
        raise RuntimeError(f"HTTPError calling Gemini: {he.code} {he.reason} {body}") from he
    except Exception as e:
        raise RuntimeError(f"Error calling Gemini API: {e}") from e

    # Defensive parsing: ensure expected keys exist
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Unexpected response structure from Gemini: {e} / response: {data}") from e


class EcoCacheClient:
    def __init__(self, api_key: str = None, similarity_threshold: float = 0.85):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key found. Set GEMINI_API_KEY in your .env file.")

        # default model name — adjust to a model available to your account
        self.model = "gemma-3-1b-it"
        # Attempt to import and initialize the real cache/metrics; fall back safely on error.
        try:
            from .cache import SemanticCache
            self.cache = SemanticCache(similarity_threshold=similarity_threshold)
        except Exception as e:
            print("Warning: failed to initialize SemanticCache, using simple in-memory fallback:", e)
            class SimpleCache:
                def __init__(self):
                    self._map = {}
                def get(self, prompt):
                    val = self._map.get(prompt)
                    return (val, 1.0) if val is not None else (None, 0.0)
                def store(self, prompt, response):
                    self._map[prompt] = response
            self.cache = SimpleCache()

        try:
            from .metrics import SavingsTracker
            self.tracker = SavingsTracker()
        except Exception as e:
            print("Warning: failed to initialize SavingsTracker, using no-op tracker:", e)
            class NoOpTracker:
                def record(self, *a, **kw): pass
                def summary(self): return {}
                def print_summary(self): pass
            self.tracker = NoOpTracker()

    def chat(self, prompt: str, **kwargs) -> dict:
        # 1. Check cache first (guarded in case cache raises)
        try:
            cached_response, similarity = self.cache.get(prompt)
        except Exception as e:
            # If cache fails unexpectedly, fall back to miss with similarity 0
            print("Warning: cache.get failed, treating as miss:", e)
            cached_response, similarity = None, 0.0

        if cached_response:
            try:
                self.tracker.record(prompt, was_cached=True, similarity=similarity)
            except Exception as e:
                print("Warning: tracker.record failed:", e)
            return {
                "response": cached_response,
                "source": "cache",
                "similarity": round(similarity, 3),
                "savings": self.tracker.summary()
            }

        # 2. Cache miss — call Gemini via plain HTTP
        print("Cache miss — calling Gemini API...")
        try:
            response_text = _call_gemini_http(prompt, self.api_key, self.model)
        except Exception as e:
            # Return a structured error instead of crashing the process
            print("Error calling Gemini API:", e)
            return {
                "response": None,
                "error": str(e),
                "source": "api",
                "similarity": 0.0,
                "savings": self.tracker.summary()
            }

        # 3. Store for future similar queries (guarded)
        try:
            self.cache.store(prompt, response_text)
        except Exception as e:
            print("Warning: cache.store failed:", e)

        # on miss similarity is unknown/zero
        try:
            self.tracker.record(prompt, was_cached=False, similarity=0.0)
        except Exception as e:
            print("Warning: tracker.record failed:", e)

        return {
            "response": response_text,
            "source": "api",
            "similarity": round(0.0, 3),
            "savings": self.tracker.summary()
        }

    def summary(self):
        self.tracker.print_summary()