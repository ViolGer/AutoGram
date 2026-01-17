from __future__ import annotations

import re
from typing import Iterable

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models import NewItem, Keyword


# Простейшие правила. Можно расширять сколько угодно.
RULES: dict[str, list[str]] = {
    "аренда": [r"\bаренд", r"\bснять\b", r"\bсда(ть|ча)\b"],
    "договор": [r"\bдоговор\b", r"\bакт\b", r"\bприложен(ие|ия)\b"],
    "залог": [r"\bзалог\b", r"\bдепозит\b"],
    "налоги": [r"\bналог", r"\bндфл\b", r"\bсамозанят", r"\bпатент\b"],
    "комиссия": [r"\bкомисси", r"\bриэлтор", r"\bагентств"],
    "мошенничество": [r"\bмошен", r"\bобман\b", r"\bразвод\b"],
}

_COMPILED = {k: [re.compile(pat, re.IGNORECASE) for pat in pats] for k, pats in RULES.items()}


def _text_of(item: NewItem) -> str:
    return "\n".join(filter(None, [item.title, item.summary, item.raw_text or ""]))


def _infer_keywords(text: str) -> list[str]:
    found: list[str] = []
    for kw, pats in _COMPILED.items():
        if any(p.search(text) for p in pats):
            found.append(kw)
    return found


def autotag_newitems(
    session: Session,
    limit: int = 200,
    only_untagged: bool = True,
) -> dict:
    q = select(NewItem).options(selectinload(NewItem.keywords)).order_by(NewItem.published_at.desc()).limit(limit)
    items = session.exec(q).all()

    updated = 0
    scanned = 0

    for item in items:
        scanned += 1

        existing = {k.word for k in (item.keywords or [])}
        if only_untagged and existing:
            continue

        text = _text_of(item)
        predicted = _infer_keywords(text)
        if not predicted:
            continue

        # создаём/берём Keyword объекты
        kw_objs: list[Keyword] = []
        for word in predicted:
            obj = session.exec(select(Keyword).where(Keyword.word == word)).first()
            if not obj:
                obj = Keyword(word=word)
                session.add(obj)
                session.flush()
            kw_objs.append(obj)

        item.keywords = kw_objs
        session.add(item)
        updated += 1

    session.commit()
    return {"scanned": scanned, "updated": updated}
