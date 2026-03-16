from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # This model is 80MB, runs on CPU, no GPU needed
        # Converts any text into a 384-number vector
        # that captures the *meaning* of the text
        print("Loading embedding model... (only happens once)")
        self.model = SentenceTransformer(model_name)
        print("Model ready.")

    def embed(self, text: str) -> np.ndarray:
        """Convert a string into a 384-dimensional vector."""
        vector = self.model.encode(text, convert_to_numpy=True)
        # Normalize so similar sentences score close to 1.0
        vector = vector / np.linalg.norm(vector)
        return vector.astype("float32")