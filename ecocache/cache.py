import faiss
import numpy as np
import json
import os
from datetime import datetime
from .embedder import Embedder

class SemanticCache:
    def __init__(self, similarity_threshold=0.85, cache_file="cache_store.json"):
        self.embedder = Embedder()
        self.threshold = similarity_threshold
        self.cache_file = cache_file

        # FAISS index — stores all query vectors for fast lookup
        # 384 = size of vectors from all-MiniLM-L6-v2
        self.dimension = 384
        self.index = faiss.IndexFlatIP(self.dimension)  # IP = Inner Product = cosine similarity on normalized vectors

        # Parallel list: position in index → stored data
        self.stored_entries = []

        # Load existing cache from disk if it exists
        self._load_from_disk()

    def get(self, query: str):
        """
        Check if a semantically similar query exists in cache.
        Returns (response, similarity_score) if found, else (None, 0).
        """
        if self.index.ntotal == 0:
            return None, 0.0

        query_vector = self.embedder.embed(query)
        query_vector = np.array([query_vector])  # FAISS needs a 2D array

        # Search for the single most similar vector
        distances, indices = self.index.search(query_vector, k=1)

        similarity = float(distances[0][0])
        best_idx = int(indices[0][0])

        if similarity >= self.threshold:
            entry = self.stored_entries[best_idx]
            print(f"Cache HIT — similarity: {similarity:.3f}")
            return entry["response"], similarity

        print(f"Cache MISS — best similarity was only: {similarity:.3f}")
        return None, similarity

    def store(self, query: str, response: str):
        """Store a new query-response pair in the cache."""
        vector = self.embedder.embed(query)

        self.index.add(np.array([vector]))
        self.stored_entries.append({
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })

        self._save_to_disk()
        print(f"Stored in cache. Total entries: {len(self.stored_entries)}")

    def _save_to_disk(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.stored_entries, f, indent=2)
        faiss.write_index(self.index, self.cache_file + ".faiss")

    def _load_from_disk(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                self.stored_entries = json.load(f)
            print(f"Loaded {len(self.stored_entries)} entries from disk cache.")
        if os.path.exists(self.cache_file + ".faiss"):
            self.index = faiss.read_index(self.cache_file + ".faiss")