from ecocache.cache import SemanticCache
from ecocache.metrics import SavingsTracker
import os

# Create once, reuse across all tests
CACHE = None

def get_cache():
    global CACHE
    if CACHE is None:
        CACHE = SemanticCache(similarity_threshold=0.80, cache_file="test_cache.json")
    return CACHE

def test_cache_hit():
    cache = get_cache()
    cache.store("What is photosynthesis?", "Plants convert sunlight to energy.")
    response, score = cache.get("Explain how photosynthesis works")
    assert response is not None, "Should have been a cache hit"
    assert score > 0.80, f"Score too low: {score}"
    print(f"PASS — cache hit with score {score:.3f}")

def test_cache_miss():
    cache = get_cache()
    response, score = cache.get("What is the capital of Mars?")
    assert response is None, "Should have been a cache miss"
    print(f"PASS — cache miss correctly returned None")

def test_metrics():
    tracker = SavingsTracker(metrics_file="test_savings.json")
    tracker.record("test query", was_cached=True, similarity=0.9)
    s = tracker.summary()
    assert s["cache_hits"] >= 1
    assert s["water_saved_ml"] > 0
    print(f"PASS — metrics tracking works, water saved: {s['water_saved_ml']}mL")

def cleanup():
    for f in ["test_cache.json", "test_cache.json.faiss", "test_savings.json"]:
        if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    print("Running tests...")
    cleanup()
    test_cache_hit()
    test_cache_miss()
    test_metrics()
    cleanup()
    print("\nAll tests passed!")