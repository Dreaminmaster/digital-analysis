from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Protocol
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .base import ProviderError, SignalProvider

_ddg_lock = threading.Lock()
_ddg_last_request: float = 0.0
_DDG_MIN_INTERVAL: float = 2.0


class SearchHttpClient(Protocol):
    def fetch(self, url: str, *, headers: dict[str, str] | None = None) -> str: ...


@dataclass
class UrllibSearchClient:
    timeout_seconds: float = 20.0
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    user_agent: str = "digital-analysis/0.1"

    def fetch(self, url: str, *, headers: dict[str, str] | None = None) -> str:
        hdrs = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        if headers:
            hdrs.update(headers)
        req = Request(url, headers=hdrs)
        last_error: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                with urlopen(req, timeout=self.timeout_seconds) as resp:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    return resp.read().decode(charset, errors="replace")
            except HTTPError:
                raise
            except (URLError, TimeoutError) as exc:
                last_error = exc
                if attempt >= self.retry_attempts:
                    break
                time.sleep(self.retry_delay_seconds)
        raise ProviderError(f"web fetch failed: {url}") from last_error


class _TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag: str):
        if tag in ("script", "style", "noscript"):
            self._skip = False
        if tag in ("p", "br", "div", "li", "tr", "h1", "h2", "h3"):
            self._pieces.append("\n")

    def handle_data(self, data: str):
        if not self._skip:
            self._pieces.append(data)

    def get_text(self) -> str:
        lines = (line.strip() for line in "".join(self._pieces).splitlines())
        return "\n".join(line for line in lines if line)


class _DuckDuckGoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] = {}
        self._capture: str | None = None

    def handle_starttag(self, tag: str, attrs):
        attr_dict = dict(attrs)
        cls = attr_dict.get("class", "") or ""
        if tag == "a" and "result__a" in cls:
            self._flush()
            href = attr_dict.get("href", "")
            if href:
                self._current["url"] = href
            self._capture = "title"
            self._current.setdefault("title", "")
        if tag == "a" and "result__snippet" in cls:
            self._capture = "snippet"
            self._current.setdefault("snippet", "")

    def handle_endtag(self, tag: str):
        if tag == "a" and self._capture in ("title", "snippet"):
            self._capture = None

    def handle_data(self, data: str):
        if self._capture == "title":
            self._current["title"] = self._current.get("title", "") + data
        elif self._capture == "snippet":
            self._current["snippet"] = self._current.get("snippet", "") + data

    def _flush(self):
        if self._current.get("url") and self._current.get("title"):
            self.results.append(self._current)
            self._current = {}

    def close(self):
        self._flush()
        super().close()


@dataclass(frozen=True)
class WebSearchQuery:
    query: str
    max_results: int = 5


@dataclass(frozen=True)
class WebSearchSnippet:
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class WebSearchResult:
    query: str
    snippets: tuple[WebSearchSnippet, ...]
    fetched_at: str


@dataclass(frozen=True)
class WebPageContent:
    url: str
    text: str


class WebSearchProvider(SignalProvider):
    provider_id = "web"
    display_name = "Web Search"
    capabilities = ("search", "page_fetch")

    def __init__(self, http_client: SearchHttpClient | None = None):
        self.http_client = http_client or UrllibSearchClient()

    def search(self, query: str | WebSearchQuery) -> WebSearchResult:
        if isinstance(query, str):
            query = WebSearchQuery(query=query)
        html = self._ddg_search(query.query)
        parser = _DuckDuckGoParser()
        parser.feed(html)
        parser.close()
        rows = parser.results[: query.max_results]
        snippets = tuple(WebSearchSnippet(title=r.get("title", ""), url=r.get("url", ""), snippet=r.get("snippet", "")) for r in rows)
        return WebSearchResult(query=query.query, snippets=snippets, fetched_at=datetime.now(timezone.utc).isoformat())

    def fetch_page(self, url: str) -> WebPageContent:
        html = self.http_client.fetch(url)
        stripper = _TagStripper()
        stripper.feed(html)
        return WebPageContent(url=url, text=stripper.get_text())

    def _ddg_search(self, query: str) -> str:
        global _ddg_last_request
        with _ddg_lock:
            now = time.monotonic()
            wait = _DDG_MIN_INTERVAL - (now - _ddg_last_request)
            if wait > 0:
                time.sleep(wait)
            _ddg_last_request = time.monotonic()
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        return self.http_client.fetch(url)
