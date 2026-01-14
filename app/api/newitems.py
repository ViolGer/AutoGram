import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.deps import get_session
from app.models import NewItem

router = APIRouter(prefix="/api/newitems", tags=["newitems"])


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
