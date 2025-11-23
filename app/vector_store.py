from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from .models import Product


class ProductVectorStore:
    def __init__(self, products: List[Product], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.products = products
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.index = None
        self._build_index()

    def _product_text(self, p: Product) -> str:
        return " ".join([
            p.name,
            p.description,
            " ".join(p.constructs),
            " ".join(p.job_families),
            " ".join(p.job_levels),
            " ".join(p.use_cases),
        ])

    def _build_index(self):
        if not self.products:
            return
        texts = [self._product_text(p) for p in self.products]
        self.embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

    def search(self, query_text: str, top_k: int = 10) -> List[Tuple[Product, float]]:
        if not query_text.strip() or self.index is None:
            return []
        q_emb = self.model.encode([query_text], convert_to_numpy=True, normalize_embeddings=True)
        scores, indices = self.index.search(q_emb, top_k)
        scores = scores[0]
        indices = indices[0]

        results = []
        for idx, score in zip(indices, scores):
            if idx == -1:
                continue
            p = self.products[idx]
            results.append((p, float(score)))
        return results
