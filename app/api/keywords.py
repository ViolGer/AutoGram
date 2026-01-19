from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.schemas import KeywordCreate, KeywordRead
from app.db.deps import get_session
from app.models import Keyword

router = APIRouter(prefix="/api/keywords", tags=["keywords"])


@router.post("", response_model=KeywordRead, status_code=status.HTTP_201_CREATED)
def create_keyword(payload: KeywordCreate, session: Session = Depends(get_session)):
    # защита от дублей (простая)
    existing = session.exec(select(Keyword).where(Keyword.word == payload.word)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Keyword already exists")

    keyword = Keyword(word=payload.word)
    session.add(keyword)
    session.commit()
    session.refresh(keyword)
    return keyword


@router.get("", response_model=List[KeywordRead])
def list_keywords(session: Session = Depends(get_session)):
    return session.exec(select(Keyword)).all()


@router.get("/{keyword_id}", response_model=KeywordRead)
def get_keyword(keyword_id: UUID, session: Session = Depends(get_session)):
    keyword = session.get(Keyword, keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(keyword_id: UUID, session: Session = Depends(get_session)):
    keyword = session.get(Keyword, keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    session.delete(keyword)
    session.commit()
    return None
