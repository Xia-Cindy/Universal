from typing import Any


def evidence_source(result: dict[str, Any], *, source_url: str | None = None) -> dict[str, Any]:
    """Normalize a retrieval result into the public Citation/Evidence contract."""
    identifiers = result.get("identifiers", {})
    identifiers = identifiers if isinstance(identifiers, dict) else {}
    metadata = result.get("metadata", {})
    metadata = metadata if isinstance(metadata, dict) else {}
    document_id = str(result.get("documentId") or identifiers.get("documentId") or "")
    chunk_id = str(result.get("chunkId") or identifiers.get("chunkId") or "")
    return {
        "sourceId": f"{document_id}:{chunk_id}",
        "documentId": document_id,
        "chunkId": chunk_id,
        "title": str(metadata.get("fileName") or metadata.get("documentName") or "Knowledge source"),
        "quote": str(result.get("content") or ""),
        "score": float(result.get("score") or 0),
        "metadata": metadata,
        "sourceUrl": source_url or (
            f"/study/knowledge?documentId={document_id}#chunk-{chunk_id}" if document_id else None
        ),
    }


def evidence_sources(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [evidence_source(result) for result in results if isinstance(result, dict)]
