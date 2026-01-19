import uuid
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db.deps import get_session
from app.models import NewItem, NewItemRead, Keyword, NewItemKeywordLink, NewItemKeywordsUpdate

from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select, or_

from sqlalchemy.orm import selectinload


router = APIRouter(prefix="/api/newitems", tags=["newitems"])


@router.get("/search", response_model=list[NewItemRead])
def search_newitems(
    query_text: Optional[str] = Query(default=None, min_length=2, description="Поиск по title/summary/raw_text"),
    source_name: Optional[str] = Query(default=None, description="Фильтр по источнику, например ProArendu"),
    keywords: Optional[list[str]] = Query(default=None, description="Список keywords: ?keywords=a&keywords=b"),
    match_all: bool = Query(default=False, description="Если true — нужны ВСЕ keywords, иначе любой из списка"),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    statement = select(NewItem).options(selectinload(NewItem.keywords))

    if source_name:
        statement = statement.where(NewItem.source == source_name)

    if query_text:
        pattern = f"%{query_text}%"
        statement = statement.where(
            or_(
                NewItem.title.ilike(pattern),
                NewItem.summary.ilike(pattern),
                NewItem.raw_text.ilike(pattern),
            )
        )

    if keywords:
        cleaned = [k.strip().lower() for k in keywords if k and k.strip()]
        cleaned_unique = list(dict.fromkeys(cleaned))

        if cleaned_unique:
            base = (
                statement
                .join(NewItemKeywordLink, NewItemKeywordLink.newitem_id == NewItem.id)
                .join(Keyword, Keyword.id == NewItemKeywordLink.keyword_id)
                .where(func.lower(Keyword.word).in_(cleaned_unique))
            )

            if match_all:
                statement = (
                    base
                    .group_by(NewItem.id)
                    .having(func.count(func.distinct(func.lower(Keyword.word))) == len(cleaned_unique))
                )
            else:
                statement = base.distinct()

    statement = statement.order_by(NewItem.published_at.desc()).limit(limit)
    items = session.exec(statement).all()

    # конвертация Keyword -> list[str] для NewItemRead
    return [
        NewItemRead(
            id=item.id,
            title=item.title,
            url=item.url,
            summary=item.summary,
            source=item.source,
            published_at=item.published_at,
            raw_text=item.raw_text,
            keywords=[k.word for k in (item.keywords or [])],
        )
        for item in items
    ]


@router.put("/{news_id}/keywords", response_model=NewItemRead)
def set_newitem_keywords(
    news_id: uuid.UUID,
    payload: NewItemKeywordsUpdate,
    session: Session = Depends(get_session),
):
    item = session.exec(
        select(NewItem)
        .where(NewItem.id == news_id)
        .options(selectinload(NewItem.keywords))
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="NewItem not found")

    # нормализуем список слов
    cleaned = [k.strip().lower() for k in (payload.keywords or []) if k and k.strip()]
    cleaned_unique = list(dict.fromkeys(cleaned))

    kw_objs: list[Keyword] = []
    for word in cleaned_unique:
        kw = session.exec(select(Keyword).where(Keyword.word == word)).first()
        if not kw:
            kw = Keyword(word=word)
            session.add(kw)
            session.flush()  # чтобы kw.id появился
        kw_objs.append(kw)

    # replace-логика: полностью перезаписываем теги
    item.keywords = kw_objs

    session.add(item)
    session.commit()
    session.refresh(item)

    # вернуть keywords в ответе
    item = session.exec(
        select(NewItem)
        .where(NewItem.id == news_id)
        .options(selectinload(NewItem.keywords))
    ).first()

    return NewItemRead(
        id=item.id,
        title=item.title,
        url=item.url,
        summary=item.summary,
        source=item.source,
        published_at=item.published_at,
        raw_text=item.raw_text,
        keywords=[k.word for k in (item.keywords or [])],
    )


@router.get("/")
def list_newitems(limit: int = 50, session: Session = Depends(get_session)):
    items = session.exec(
        select(NewItem).order_by(NewItem.published_at.desc()).limit(limit)
    ).all()
    return items


@router.get("/{news_id}")
def get_newitem(news_id: uuid.UUID, session: Session = Depends(get_session)):
    item = session.get(NewItem, news_id)
    if not item:
        raise HTTPException(status_code=404, detail="NewItem not found")
    return item
