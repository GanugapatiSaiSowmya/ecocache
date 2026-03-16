import json
import os
from datetime import datetime

# Real-world estimates from published research
# Source: University of California Riverside (2023) + IEA data
WATER_PER_INFERENCE_ML = 5.0      # ~5mL per request (conservative estimate)
CARBON_PER_INFERENCE_G = 4.0      # ~4g CO2 per request (varies by grid/region)

class SavingsTracker:
    def __init__(self, metrics_file="savings.json"):
        self.metrics_file = metrics_file
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file) as f:
                return json.load(f)
        # Fresh start
        return {
            "total_queries": 0,
            "cache_hits": 0,
            "water_saved_ml": 0.0,
            "carbon_saved_g": 0.0,
            "history": []
        }

    def record(self, query: str, was_cached: bool, similarity: float):
        """Call this every time a query comes in, hit or miss."""
        self.data["total_queries"] += 1

        if was_cached:
            self.data["cache_hits"] += 1
            self.data["water_saved_ml"] += WATER_PER_INFERENCE_ML
            self.data["carbon_saved_g"] += CARBON_PER_INFERENCE_G

        self.data["history"].append({
            "query_preview": query[:60],
            "cached": was_cached,
            "similarity": round(similarity, 3),
            "timestamp": datetime.now().isoformat()
        })

        self._save()

    def _save(self):
        with open(self.metrics_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def summary(self) -> dict:
        d = self.data
        total = d["total_queries"]
        hits = d["cache_hits"]
        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "total_queries": total,
            "cache_hits": hits,
            "hit_rate_pct": round(hit_rate, 1),
            "water_saved_ml": round(d["water_saved_ml"], 1),
            "carbon_saved_g": round(d["carbon_saved_g"], 1),
            # Make it tangible
            "water_saved_bottles": round(d["water_saved_ml"] / 500, 2),
            "carbon_equiv_km_driven": round(d["carbon_saved_g"] / 180, 3)
        }

    def print_summary(self):
        s = self.summary()
        print("\n--- EcoCache Savings ---")
        print(f"Total queries    : {s['total_queries']}")
        print(f"Cache hits       : {s['cache_hits']} ({s['hit_rate_pct']}%)")
        print(f"Water saved      : {s['water_saved_ml']} mL ({s['water_saved_bottles']} bottles)")
        print(f"Carbon avoided   : {s['carbon_saved_g']} g CO2 ({s['carbon_equiv_km_driven']} km driving equiv.)")
        print("------------------------\n")