from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session, select

from app.models import NewItem, Source


DEFAULT_HEADERS = {
    # от 403
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


def _is_http_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _normalize_link(base_url: str, href: str) -> str | None:
    if not href:
        return None
    href = href.strip()
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
        return None

    full = urljoin(base_url, href)

    if not _is_http_url(full):
        return None

    parsed = urlparse(full)
    full = parsed._replace(fragment="").geturl()
    return full


def _extract_links(html: str, base_url: str) -> list[tuple[str, str]]:

    soup = BeautifulSoup(html, "html.parser")
    items: list[tuple[str, str]] = []

    for a in soup.select("a[href]"):
        href = a.get("href")
        url = _normalize_link(base_url, href)
        if not url:
            continue

        title = (a.get_text(" ", strip=True) or "").strip()
        if not title:
            continue

        if len(title) < 12:
            continue

        items.append((title, url))

    # дедуп по url
    seen = set()
    uniq: list[tuple[str, str]] = []
    for title, url in items:
        if url in seen:
            continue
        seen.add(url)
        uniq.append((title, url))
    return uniq


def parse_html_sources(session: Session) -> dict:
    sources: list[Source] = session.exec(
        select(Source).where(Source.enabled == True, Source.type == "html")  # noqa: E712
    ).all()

    if not sources:
        return {"sources": 0, "added": 0}

    added_total = 0

    with httpx.Client(headers=DEFAULT_HEADERS, timeout=20, follow_redirects=True) as client:
        for src in sources:
            resp = client.get(src.url)
            resp.raise_for_status()

            links = _extract_links(resp.text, base_url=src.url)

            for title, url in links:
                # анти-дубль
                exists = session.exec(select(NewItem).where(NewItem.url == url)).first()
                if exists:
                    continue

                news = NewItem(
                    title=title,
                    url=url,
                    summary=title,
                    source=src.name,
                    published_at=datetime.now(timezone.utc),
                    raw_text=None,
                )
                session.add(news)
                added_total += 1

            session.commit()

    return {"sources": len(sources), "added": added_total}
