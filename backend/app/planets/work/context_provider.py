from backend.app.ai import AIContext
from backend.app.services.evidence import evidence_sources


class WorkExplorationContextProvider:
    """Build source-aware context for a selected passage in a Work Tech Stack."""

    def build(self, payload: dict) -> AIContext:
        stack = payload.get("techStack") or {}
        article = payload.get("sourceArticle") or {}
        quote = str(payload.get("selectedQuote") or "").strip()
        retrieval = payload.get("toolResults", {}).get("retrieval.search", {})
        chunks = retrieval.get("results", [])
        sources = evidence_sources(chunks)
        stack_name = str(stack.get("name") or "当前技术")
        article_title = str(article.get("title") or "当前技术条目")
        selected = quote or "未划线；请围绕当前技术条目解释问题。"
        fallback_answer = (
            f"你正在探索 {stack_name} 中《{article_title}》的这段内容：\n{selected}\n\n"
            "先把它拆成：它解决什么问题、关键边界在哪里、错误使用会带来什么后果。"
            "再把你的问题写成一个可验证的场景；若没有资料引用，这只是通用解释，需要你用来源或实践确认。"
        )
        return AIContext(
            {
                "user": payload.get("user", {}),
                "techStack": stack,
                "sourceArticle": article or None,
                "selectedQuote": quote or None,
                "allowedKnowledge": payload.get("allowedKnowledge", []),
                "knowledgeContext": {"retrievalInvoked": bool(retrieval.get("available")), "chunks": chunks},
                "responseHints": {
                    "answer": fallback_answer,
                    "reasoning": (
                        f"Prepared an exploration context for {stack_name}; "
                        f"{len(sources)} authorized Knowledge source(s) matched."
                    ),
                    "suggestedNextAction": "Edit the explanation into your own words, then save it as an exploration or design one small practice.",
                    "metadata": {
                        "retrievalInvoked": bool(retrieval.get("available")),
                        "groundingChunks": chunks,
                        "sources": sources,
                        "knowledgeSourcesAvailable": bool(sources),
                    },
                },
            }
        )
