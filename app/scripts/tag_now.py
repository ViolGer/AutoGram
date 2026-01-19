from __future__ import annotations

import re
from typing import Iterable

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.db.deps import engine
from app.models import NewItem, Keyword


# базовые теги (контролируемый словарь)
DEFAULT_KEYWORDS = [
    "аренда",
    "договор",
    "залог",
    "комиссия",
    "налоги",
    "риэлтор",
    "собственник",
    "повышение",
]

# простые синонимы/паттерны (можно расширять)
RULES: dict[str, list[str]] = {
    "аренда": [r"\bаренд", r"\bснять\b", r"\bсда(ть|ча)\b"],
    "договор": [r"\bдоговор\b", r"\bакт\b", r"\bсоглашен"],
    "залог": [r"\bзалог\b", r"\bдепозит\b"],
    "комиссия": [r"\bкомисси"],
    "налоги": [r"\bналог", r"\bндфл\b", r"\bсамозанят", r"\bпатент\b"],
    "риэлтор": [r"\bриэлтор\b", r"\bагент\b", r"\bагентств"],
    "собственник": [r"\bсобственник\b", r"\bарендодател"],
    "повышение": [r"\bповыш", r"\bиндексац"],
}

_COMPILED = {k: [re.compile(p, re.IGNORECASE) for p in pats] for k, pats in RULES.items()}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def _text_of(it: NewItem) -> str:
    return " ".join([it.title or "", it.summary or "", it.raw_text or ""])


def _infer_tags(text: str) -> list[str]:
    # возвращает список tag-слов из DEFAULT_KEYWORDS, которые нашли по RULES
    found: list[str] = []
    for tag, pats in _COMPILED.items():
        if any(p.search(text) for p in pats):
            found.append(tag)
    # оставляем только из белого списка
    allowed = set(DEFAULT_KEYWORDS)
    return [t for t in found if t in allowed]


def main(limit: int = 500, only_untagged: bool = True) -> None:
    with Session(engine) as db:
        # 1) гарантируем, что Keyword есть в таблице
        kw_map: dict[str, Keyword] = {}
        for w in DEFAULT_KEYWORDS:
            w2 = norm(w)
            obj = db.exec(select(Keyword).where(Keyword.word == w2)).first()
            if not obj:
                obj = Keyword(word=w2)
                db.add(obj)
                db.flush()  # чтобы obj получил id
            kw_map[w2] = obj
        db.commit()

        # 2) грузим items + их keywords
        q = (
            select(NewItem)
            .options(selectinload(NewItem.keywords))
            .order_by(NewItem.published_at.desc())
            .limit(limit)
        )
        items = db.exec(q).all()

        updated = 0
        scanned = 0

        for it in items:
            scanned += 1

            existing = {k.word for k in (it.keywords or [])}
            if only_untagged and existing:
                continue

            text = _text_of(it)
            t = norm(text)

            predicted = _infer_tags(t)
            if not predicted:
                continue

            # добавляем только новые
            to_add = [kw_map[w] for w in predicted if w not in existing]
            if not to_add:
                continue

            it.keywords = (it.keywords or []) + to_add
            db.add(it)
            updated += 1

        db.commit()
        print(f"Scanned: {scanned}, updated: {updated}, total: {len(items)}")


if __name__ == "__main__":
    main()
