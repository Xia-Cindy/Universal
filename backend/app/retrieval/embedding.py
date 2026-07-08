from hashlib import sha256
from typing import Protocol

from backend.app.retrieval.models import EmbeddingResult


class EmbeddingProvider(Protocol):
    provider_name: str
    model_name: str

    def embed(self, text: str) -> EmbeddingResult:
        """Return a vector for plain text."""


class DeterministicEmbeddingProvider:
    provider_name = "deterministic"
    model_name = "deterministic-small"

    def __init__(self, dimension: int = 8) -> None:
        self.dimension = dimension

    def embed(self, text: str) -> EmbeddingResult:
        digest = sha256(text.encode("utf-8")).digest()
        vector = [
            round(((digest[index] / 255.0) * 2.0) - 1.0, 6)
            for index in range(self.dimension)
        ]
        return EmbeddingResult(
            vector=vector,
            provider=self.provider_name,
            model=self.model_name,
        )

