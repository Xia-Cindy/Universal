import json
from base64 import b64decode
from binascii import Error as BinasciiError
from urllib import error, parse, request

from backend.app.models import Document


class RAGFlowAPIError(RuntimeError):
    pass


class RAGFlowClient:
    def __init__(self, *, base_url: str, api_key: str, timeout_seconds: int = 30) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
        query: dict[str, object] | None = None,
    ) -> dict[str, object]:
        url = self._url(path, query=query)
        body = json.dumps(payload or {}).encode("utf-8") if payload is not None else None
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        req = request.Request(url, data=body, headers=headers, method=method)
        return self._send(req)

    def upload_document(
        self,
        *,
        dataset_id: str,
        file_name: str,
        content: str,
        file_type: str,
        content_encoding: str = "text",
    ) -> dict[str, object]:
        boundary = "----UniverseOSRAGFlowBoundary"
        try:
            file_bytes = (
                b64decode(content, validate=True)
                if content_encoding == "base64"
                else content.encode("utf-8")
            )
        except (BinasciiError, ValueError) as exc:
            raise RAGFlowAPIError("Invalid base64 document content") from exc
        suffix = "md" if file_type == "markdown" else file_type
        upload_name = file_name if "." in file_name else f"{file_name}.{suffix}"
        body = b"".join(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                (
                    'Content-Disposition: form-data; name="file"; '
                    f'filename="{upload_name}"\r\n'
                ).encode("utf-8"),
                b"Content-Type: application/octet-stream\r\n\r\n",
                file_bytes,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        req = request.Request(
            self._url(f"/api/v1/datasets/{dataset_id}/documents"),
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )
        return self._send(req)

    def _url(self, path: str, query: dict[str, object] | None = None) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        url = f"{self._base_url}{normalized_path}"
        if query:
            filtered = {key: value for key, value in query.items() if value not in (None, "", [])}
            if filtered:
                url = f"{url}?{parse.urlencode(filtered)}"
        return url

    def _send(self, req: request.Request) -> dict[str, object]:
        try:
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                payload = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RAGFlowAPIError(f"RAGFlow HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise RAGFlowAPIError(f"RAGFlow connection failed: {exc.reason}") from exc
        if not payload:
            return {}
        data = json.loads(payload)
        if isinstance(data, dict) and data.get("code") not in (None, 0):
            raise RAGFlowAPIError(str(data.get("message", "RAGFlow request failed")))
        return data


class RAGFlowKnowledgeProvider:
    name = "ragflow"

    def __init__(
        self,
        *,
        client: RAGFlowClient,
        dataset_id: str | None = None,
        dataset_name: str = "Universe OS Knowledge",
        embedding_model: str = "",
        llm_model: str = "",
        rerank_model: str = "",
    ) -> None:
        self._client = client
        self._default_dataset_id = dataset_id
        self._dataset_name = dataset_name
        self._models = {
            "embedding": embedding_model or None,
            "llm": llm_model or None,
            "rerank": rerank_model or None,
        }
        self._dataset_ids_by_scope: dict[str, str] = {}

    def health_check(self) -> dict[str, object]:
        response = self._client.request_json(
            "GET",
            "/api/v1/datasets",
            query={"page": 1, "page_size": 1},
        )
        return {
            "provider": self.name,
            "status": "ok",
            "datasetCount": len(response.get("data", [])) if isinstance(response.get("data"), list) else 0,
            "modelConfiguration": {
                key: {"configuredByUniverse": bool(value), "model": value}
                for key, value in self._models.items()
            },
            "note": "Model execution is owned by RAGFlow; this endpoint reports only Universe-side labels and API reachability.",
        }

    def upload_document(self, *, user_id: str, document: Document) -> dict[str, object]:
        dataset_id = self._ensure_dataset(document)
        response = self._client.upload_document(
            dataset_id=dataset_id,
            file_name=document.file_name,
            content=document.content,
            file_type=document.file_type.value,
            content_encoding=document.content_encoding,
        )
        uploaded = self._first_item(response.get("data"))
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": uploaded.get("id") or uploaded.get("document_id"),
            "status": uploaded.get("run") or uploaded.get("status") or "uploaded",
            "raw": uploaded,
        }

    def parse_document(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        response = self._client.request_json(
            "POST",
            f"/api/v1/datasets/{dataset_id}/chunks",
            {"document_ids": [document_id]},
        )
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": response.get("data", {}).get("run") if isinstance(response.get("data"), dict) else "chunking",
            "raw": response,
        }

    def get_document_status(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        response = self._client.request_json(
            "GET",
            f"/api/v1/datasets/{dataset_id}/documents",
            query={"id": document_id, "page": 1, "page_size": 1},
        )
        data = response.get("data", [])
        if isinstance(data, dict):
            documents = data.get("docs", [])
            item = documents[0] if isinstance(documents, list) and documents else {}
        else:
            item = data[0] if isinstance(data, list) and data else data
        if not isinstance(item, dict):
            raise RAGFlowAPIError("RAGFlow did not return document status")
        run = str(item.get("run") or item.get("status") or "unknown").lower()
        progress_message = item.get("progress_msg")
        error_message = item.get("fail_reason") or item.get("error_message") or progress_message
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": run,
            "errorMessage": error_message,
            "errorCode": _ragflow_error_code(str(error_message or "")),
            "progressMessage": progress_message,
            "raw": item,
        }

    def delete_document(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
    ) -> dict[str, object]:
        response = self._client.request_json(
            "DELETE",
            f"/api/v1/datasets/{dataset_id}/documents",
            {"ids": [document_id]},
        )
        return {
            "provider": self.name,
            "datasetId": dataset_id,
            "documentId": document_id,
            "status": "deleted",
            "raw": response,
        }

    def list_document_chunks(
        self,
        *,
        user_id: str,
        dataset_id: str,
        document_id: str,
        limit: int = 30,
    ) -> list[dict[str, object]]:
        response = self._client.request_json(
            "GET",
            f"/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks",
            query={"page": 1, "page_size": limit},
        )
        data = response.get("data", {})
        chunks = data.get("chunks", []) if isinstance(data, dict) else []
        return [
            {
                "chunkId": chunk.get("id"),
                "documentId": chunk.get("document_id") or document_id,
                "content": chunk.get("content", ""),
                "metadata": {
                    "provider": self.name,
                    "datasetId": dataset_id,
                    "documentId": document_id,
                    "available": chunk.get("available", True),
                    "importantKeywords": chunk.get("important_keywords", []),
                },
            }
            for chunk in chunks
        ]

    def search(
        self,
        *,
        user_id: str,
        query: str,
        dataset_ids: list[str],
        document_ids: list[str] | None = None,
        limit: int = 5,
    ) -> dict[str, object]:
        response = self._client.request_json(
            "POST",
            "/api/v1/retrieval",
            {
                "question": query,
                "dataset_ids": dataset_ids,
                "document_ids": document_ids or [],
                "page": 1,
                "page_size": limit,
            },
        )
        data = response.get("data", {})
        chunks = data.get("chunks", []) if isinstance(data, dict) else []
        results = [
            {
                "documentId": chunk.get("document_id") or chunk.get("doc_id"),
                "chunkId": chunk.get("id") or chunk.get("chunk_id"),
                "content": chunk.get("content", ""),
                "metadata": {
                    "provider": self.name,
                    "datasetId": chunk.get("dataset_id"),
                    "documentName": chunk.get("docnm_kwd") or chunk.get("document_name"),
                    "positions": chunk.get("positions", []),
                },
                "score": float(chunk.get("similarity") or chunk.get("score") or 0),
                "identifiers": {
                    "provider": self.name,
                    "datasetId": chunk.get("dataset_id"),
                    "documentId": chunk.get("document_id") or chunk.get("doc_id"),
                    "chunkId": chunk.get("id") or chunk.get("chunk_id"),
                },
            }
            for chunk in chunks
        ]
        return {"query": query, "results": results}

    def _ensure_dataset(self, document: Document | None = None) -> str:
        scope_key, dataset_name = self._dataset_scope(document)
        if scope_key == "global" and self._default_dataset_id:
            return self._default_dataset_id
        if scope_key in self._dataset_ids_by_scope:
            return self._dataset_ids_by_scope[scope_key]
        existing = self._find_dataset(dataset_name)
        if existing:
            self._dataset_ids_by_scope[scope_key] = existing
            return existing
        response = self._client.request_json(
            "POST",
            "/api/v1/datasets",
            {"name": dataset_name},
        )
        data = response.get("data", {})
        if not isinstance(data, dict) or not data.get("id"):
            raise RAGFlowAPIError("RAGFlow did not return a dataset id")
        dataset_id = str(data["id"])
        self._dataset_ids_by_scope[scope_key] = dataset_id
        return dataset_id

    def _find_dataset(self, dataset_name: str) -> str | None:
        response = self._client.request_json(
            "GET",
            "/api/v1/datasets",
            query={"page": 1, "page_size": 100},
        )
        data = response.get("data", [])
        if isinstance(data, dict):
            data = data.get("docs") or data.get("datasets") or data.get("items") or []
        if not isinstance(data, list):
            return None
        for item in data:
            if isinstance(item, dict) and item.get("name") == dataset_name and item.get("id"):
                return str(item["id"])
        return None

    def _dataset_scope(self, document: Document | None = None) -> tuple[str, str]:
        if document and document.goal_id:
            goal_id = str(document.goal_id)
            goal_name = _display_scope_name(document.scope_name, fallback=goal_id[:8])
            return (
                f"study-goal:{goal_id}",
                f"{self._dataset_name} / Study / {goal_name} ({goal_id[:8]})",
            )
        if document and document.planet_type == "work" and document.tech_stack_id:
            tech_stack_id = str(document.tech_stack_id)
            tech_stack_name = _display_scope_name(document.scope_name, fallback=tech_stack_id[:8])
            return (
                f"work-tech-stack:{tech_stack_id}",
                f"{self._dataset_name} / Work / {tech_stack_name} ({tech_stack_id[:8]})",
            )
        if document and document.planet_type == "work":
            return ("work", f"{self._dataset_name} / Work")
        return ("global", self._dataset_name)

    def _first_item(self, value: object) -> dict[str, object]:
        if isinstance(value, list) and value:
            item = value[0]
            return item if isinstance(item, dict) else {}
        if isinstance(value, dict):
            return value
        return {}


def _display_scope_name(value: str | None, *, fallback: str) -> str:
    normalized = " ".join((value or "").split()).strip()
    return normalized[:120] or fallback


def _ragflow_error_code(message: str) -> str | None:
    if "InvalidApiKey" in message or "Invalid API-key" in message:
        return "RAGFLOW_EMBEDDING_INVALID_API_KEY"
    if "bind embedding model" in message.lower():
        return "RAGFLOW_EMBEDDING_MODEL_BIND_FAILED"
    return None
