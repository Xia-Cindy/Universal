import html
import re
from dataclasses import dataclass
from urllib import error, request


@dataclass(frozen=True)
class CommunityArticle:
    title: str
    url: str
    source: str = "CSDN"
    heat: str = ""
    summary: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "heat": self.heat,
            "summary": self.summary,
        }


class CSDNCommunityService:
    """Fetches public CSDN topic articles without coupling Work to Knowledge/RAG."""

    def __init__(self, *, timeout_seconds: int = 8) -> None:
        self._timeout_seconds = timeout_seconds

    def hot_articles(self, topic: str = "java", limit: int = 30) -> dict[str, object]:
        normalized_topic = self._normalize_topic(topic)
        url = f"https://blog.csdn.net/nav/{normalized_topic}"
        try:
            articles = self._fetch_articles(url, limit=limit)
            return {
                "source": "CSDN",
                "topic": normalized_topic,
                "url": url,
                "articles": [article.to_dict() for article in articles[:limit]],
                "error": "",
            }
        except (OSError, ValueError) as exc:
            return {
                "source": "CSDN",
                "topic": normalized_topic,
                "url": url,
                "articles": [],
                "error": str(exc),
            }

    def _fetch_articles(self, url: str, *, limit: int) -> list[CommunityArticle]:
        req = request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 UniverseOS/0.1",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                content = response.read().decode("utf-8", errors="replace")
        except error.URLError as exc:
            raise OSError(f"CSDN community fetch failed: {exc.reason}") from exc
        articles = self.parse_articles(content, limit=limit)
        if not articles:
            raise ValueError("CSDN community page did not expose article cards")
        return articles

    def parse_articles(self, content: str, *, limit: int = 30) -> list[CommunityArticle]:
        candidates: list[CommunityArticle] = []
        seen: set[str] = set()
        for match in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', content, re.S | re.I):
            href = html.unescape(match.group(1))
            body = re.sub(r"<[^>]+>", " ", match.group(2))
            title = " ".join(html.unescape(body).split())
            if not title or len(title) < 8:
                continue
            if "blog.csdn.net" not in href and not href.startswith("/"):
                continue
            if href.startswith("/"):
                href = f"https://blog.csdn.net{href}"
            if href in seen:
                continue
            seen.add(href)
            candidates.append(CommunityArticle(title=title[:120], url=href))
            if len(candidates) >= limit:
                break
        return candidates

    def _normalize_topic(self, topic: str) -> str:
        normalized = topic.strip().lower().replace(" ", "")
        if not normalized:
            return "java"
        aliases = {
            "人工智能": "ai",
            "后端": "backend",
            "前端": "web",
            "大数据": "bigdata",
        }
        return aliases.get(normalized, re.sub(r"[^a-z0-9_-]", "", normalized) or "java")
