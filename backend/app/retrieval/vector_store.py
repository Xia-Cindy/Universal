from dataclasses import dataclass
from math import sqrt
from typing import Any, Protocol


@dataclass(frozen=True)
class VectorMatch:
    vector_ref: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    def upsert(self, *, vector_ref: str, vector: list[float], payload: dict[str, Any]) -> str:
        """Store or replace a vector."""

    def search(
        self,
        *,
        query_vector: list[float],
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorMatch]:
        """Return ranked vector matches."""


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._vectors: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def upsert(self, *, vector_ref: str, vector: list[float], payload: dict[str, Any]) -> str:
        self._vectors[vector_ref] = (vector, payload)
        return vector_ref

    def search(
        self,
        *,
        query_vector: list[float],
        limit: int,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorMatch]:
        matches: list[VectorMatch] = []
        for vector_ref, (vector, payload) in self._vectors.items():
            if filters and any(
                (
                    payload.get("documentId") not in value
                    if key == "documentIds"
                    else payload.get(key) != value
                )
                for key, value in filters.items()
            ):
                continue
            matches.append(
                VectorMatch(
                    vector_ref=vector_ref,
                    score=_cosine_similarity(query_vector, vector),
                    payload=payload,
                )
            )
        return sorted(matches, key=lambda match: match.score, reverse=True)[:limit]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return round(dot / (left_norm * right_norm), 6)
