import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.deps import get_session
from app.models import NewItem

from typing import Optional
from fastapi import Query
from sqlmodel import Session, select, or_


router = APIRouter(prefix="/api/newitems", tags=["newitems"])


@router.get("/search")
def search_newitems(
    query_text: Optional[str] = Query(default=None, min_length=2, description="Поиск по title/summary"),
    source_name: Optional[str] = Query(default=None, description="Фильтр по источнику, например ProArendu"),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    statement = select(NewItem)

    # фильтр по источнику
    if source_name:
        statement = statement.where(NewItem.source == source_name)

    # фильтр по тексту (в заголовке или саммари)
    if query_text:
        pattern = f"%{query_text}%"
        statement = statement.where(
            or_(
                NewItem.title.like(pattern),
                NewItem.summary.like(pattern),
            )
        )

    statement = statement.order_by(NewItem.published_at.desc()).limit(limit)

    results = session.exec(statement).all()
    return results



@router.get("")
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
