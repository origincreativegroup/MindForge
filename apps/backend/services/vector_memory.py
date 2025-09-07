from __future__ import annotations

"""Vector-based memory layer for Casey conversations.

The implementation provides a thin abstraction over external vector
stores such as Pinecone or Weaviate while falling back to a simple
in-memory list when those services are unavailable.  Embeddings are
retrieved from the OpenAI API.
"""

import math
import os

import httpx

try:  # Optional dependencies
    import pinecone
except Exception:  # pragma: no cover - optional
    pinecone = None

try:  # Optional dependencies
    import weaviate
except Exception:  # pragma: no cover - optional
    weaviate = None

from .llm_client import BASE_URL, TIMEOUT, _auth_headers

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_URL = f"{BASE_URL or 'https://api.openai.com'}/v1/embeddings"


def _embed(text: str) -> list[float]:
    payload = {"input": text, "model": EMBED_MODEL}
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(EMBED_URL, headers=_auth_headers(), json=payload)
        r.raise_for_status()
        data = r.json()
        return data["data"][0]["embedding"]


class VectorMemory:
    """Store and retrieve conversation snippets via vector similarity."""

    def __init__(self, index_name: str = "casey-memory", dimension: int = 1536):
        self.provider = os.getenv("VECTOR_DB", "").lower()
        self.index_name = index_name
        if self.provider == "pinecone" and pinecone:
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY", ""),
                environment=os.getenv("PINECONE_ENV", ""),
            )
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(name=index_name, dimension=dimension)
            self.index = pinecone.Index(index_name)
        elif self.provider == "weaviate" and weaviate:
            url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
            self.client = weaviate.Client(url)
            self.index = index_name
        else:
            self.store: list[tuple[str, list[float], str]] = []

    # ------------------------------------------------------------------
    def add(self, conv_id: str, text: str) -> None:
        vec = _embed(text)
        if self.provider == "pinecone" and pinecone:
            self.index.upsert([(conv_id, vec, {"text": text})])
        elif self.provider == "weaviate" and weaviate:
            self.client.batch.add_data_object(
                {"conversation": conv_id, "text": text},
                class_name=self.index,
                vector=vec,
            )
        else:
            self.store.append((conv_id, vec, text))

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> list[str]:
        vec = _embed(query)
        if self.provider == "pinecone" and pinecone:
            res = self.index.query(vec, top_k=top_k, include_metadata=True)
            return [m["metadata"]["text"] for m in res.get("matches", [])]
        elif self.provider == "weaviate" and weaviate:
            result = (
                self.client.query.get(self.index, ["text"])
                .with_near_vector({"vector": vec})
                .with_limit(top_k)
                .do()
            )
            return [r["text"] for r in result["data"]["Get"].get(self.index, [])]
        else:
            # naive cosine similarity
            def cosine(u: list[float], v: list[float]) -> float:
                dot = sum(a * b for a, b in zip(u, v, strict=False))
                nu = math.sqrt(sum(a * a for a in u))
                nv = math.sqrt(sum(b * b for b in v))
                return dot / (nu * nv + 1e-10)

            scored = [(cosine(vec, v), text) for _cid, v, text in self.store]
            scored.sort(reverse=True)
            return [text for _s, text in scored[:top_k]]
