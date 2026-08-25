from backend.app.ai import AICoreService, AIRequest
from backend.app.services.evidence import evidence_sources
from backend.app.users.service import UserProfile


class WorkExplorationService:
    """Work-owned learning exploration that consumes the one shared AI Core."""

    def __init__(self, *, ai_core: AICoreService) -> None:
        self._ai_core = ai_core

    def ask(
        self,
        *,
        user: UserProfile,
        tech_stack: dict[str, object],
        source_article: dict[str, object] | None,
        selected_quote: str,
        question: str,
        allowed_documents: list[dict[str, object]],
    ) -> dict[str, object]:
        normalized_question = question.strip()
        normalized_quote = selected_quote.strip()
        if not normalized_question:
            raise ValueError("question is required")
        if len(normalized_question) > 2000:
            raise ValueError("question must be 2000 characters or fewer")
        if len(normalized_quote) > 4000:
            raise ValueError("selectedQuote must be 4000 characters or fewer")

        response = self._ai_core.run(
            AIRequest(
                agent_id="work",
                capability="explore",
                user_question=normalized_question,
                context_payload={
                    "user": user.to_dict(),
                    "techStack": tech_stack,
                    "sourceArticle": source_article,
                    "selectedQuote": normalized_quote,
                    "allowedKnowledge": [
                        {
                            "id": document["id"],
                            "fileName": document.get("fileName", "Knowledge source"),
                            "accessMode": document.get("accessMode", "owned"),
                        }
                        for document in allowed_documents
                    ],
                },
                tool_payloads=(
                    {
                        "retrieval.search": {
                            "userId": user.id,
                            "query": normalized_question,
                            "limit": 3,
                            "documentIds": [str(document["id"]) for document in allowed_documents],
                        }
                    }
                    if allowed_documents
                    else {}
                ),
            )
        )
        payload = response.to_dict()
        grounding_chunks = payload.get("groundingChunks", [])
        sources = payload.get("sources") or evidence_sources(grounding_chunks)
        payload["sources"] = sources
        payload["sourceArticleId"] = source_article.get("id") if source_article else None
        payload["selectedQuote"] = normalized_quote
        payload["knowledgeSourcesAvailable"] = bool(sources)
        payload["sourceNotice"] = (
            "回答引用了当前技术栈已授权的共享 Knowledge。"
            if sources
            else "本次没有匹配到已授权的共享 Knowledge；回答仅供继续学习，不是个人资料引用。"
        )
        return payload
