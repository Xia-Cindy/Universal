import html
import re
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib import error, request


@dataclass(frozen=True)
class CommunityArticle:
    title: str
    url: str
    source: str = "CSDN"
    heat: str = ""
    summary: str = ""
    content: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "heat": self.heat,
            "summary": self.summary,
            "content": self.content,
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
            if len(articles) < limit:
                articles.extend(self._fallback_articles(normalized_topic, limit - len(articles)))
            return {
                "source": "CSDN",
                "topic": normalized_topic,
                "url": url,
                "articles": [article.to_dict() for article in articles[:limit]],
                "error": "",
            }
        except (OSError, ValueError) as exc:
            articles = self._fallback_articles(normalized_topic, limit)
            return {
                "source": "CSDN",
                "topic": normalized_topic,
                "url": url,
                "articles": [article.to_dict() for article in articles],
                "error": "",
                "notice": str(exc),
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

    def article_detail(self, url: str) -> dict[str, str]:
        if not self._is_csdn_article_url(url):
            return {
                "title": "",
                "url": url,
                "content": "",
                "error": "Only CSDN article detail pages can be read inside Universe OS.",
            }
        try:
            content = self._fetch_html(url)
            return {**self.parse_article_detail(content, url=url), "error": ""}
        except (OSError, ValueError) as exc:
            return {
                "title": "",
                "url": url,
                "content": "",
                "error": str(exc),
            }

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

    def parse_article_detail(self, content: str, *, url: str) -> dict[str, str]:
        title = self._extract_title(content)
        article_match = re.search(
            r'<article[^>]*>(.*?)</article>|<div[^>]+(?:id|class)="[^"]*(?:content_views|article_content|blog-content-box)[^"]*"[^>]*>(.*?)</div>',
            content,
            re.S | re.I,
        )
        raw_body = next((group for group in article_match.groups() if group), "") if article_match else content
        text = self._html_to_text(raw_body)
        if not text:
            raise ValueError("CSDN article content is unavailable for inline reading")
        return {
            "title": title,
            "url": url,
            "content": text[:3000],
        }

    def _fallback_articles(self, topic: str, limit: int) -> list[CommunityArticle]:
        seeds = [
            "Java核心技术：Java获取反射的三种方法",
            "从一个传文件的需求到 Spring Boot 公网部署实践",
            "飞算JavaAI 智能引导背后的多 Agent 协作机制解析",
            "JDK 下载安装与环境配置全教程",
            "大模型流式网关：Java 后端别把 SSE 当简单转发",
            "JavaSE 总复习：语法到多线程全梳理",
            "从 HTTP 调用到工程体系：Java 集成大模型的全链路最佳实践",
            "Spring Boot 项目热部署配置",
            "Linux 环境开发工具使用：vim、gcc、make",
            "Spring AI 框架实战与工程落地",
        ]
        articles = []
        search_url = f"https://so.csdn.net/so/search?q={topic}&t=blog"
        for index in range(limit):
            title = seeds[index % len(seeds)] if topic == "java" else f"{topic} 技术社区热文 {index + 1}"
            suffix = "" if index < len(seeds) else f" #{index + 1}"
            articles.append(
                CommunityArticle(
                    title=f"{title}{suffix}",
                    url=search_url,
                    heat="community",
                    summary="CSDN community discovery fallback. 本地无法读取实时正文时，先保留这个社区发现入口。",
                    content="当前本地服务没有拿到 CSDN 实时正文。这条内容用于占位展示社区发现流，后续网络可用时会替换成实际文章预览。",
                )
            )
        return articles

    def _fetch_html(self, url: str) -> str:
        req = request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 UniverseOS/0.1",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with request.urlopen(req, timeout=self._timeout_seconds) as response:
                return response.read().decode("utf-8", errors="replace")
        except error.URLError as exc:
            raise OSError(f"CSDN article fetch failed: {exc.reason}") from exc

    def _extract_title(self, content: str) -> str:
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S | re.I)
        if not title_match:
            title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.S | re.I)
        if not title_match:
            return ""
        return self._html_to_text(title_match.group(1)).replace("-CSDN博客", "").strip()

    def _html_to_text(self, content: str) -> str:
        cleaned = re.sub(r"<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", " ", content, flags=re.S | re.I)
        cleaned = re.sub(r"<br\s*/?>|</p>|</div>|</h\d>|</li>", "\n", cleaned, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        lines = [" ".join(html.unescape(line).split()) for line in cleaned.splitlines()]
        return "\n".join(line for line in lines if line)

    def _is_csdn_article_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc.endswith("csdn.net") and "/article/details/" in parsed.path

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
