from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.schemas import SourceCreate, SourceUpdate, SourceRead
from app.db.deps import get_session
from app.models import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
def create_source(payload: SourceCreate, session: Session = Depends(get_session)):
    source = Source(**payload.model_dump())
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.get("", response_model=List[SourceRead])
def list_sources(session: Session = Depends(get_session)):
    sources = session.exec(select(Source)).all()
    return sources


@router.get("/{source_id}", response_model=SourceRead)
def get_source(source_id: UUID, session: Session = Depends(get_session)):
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.patch("/{source_id}", response_model=SourceRead)
def update_source(source_id: UUID, payload: SourceUpdate, session: Session = Depends(get_session)):
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(source, key, value)

    session.add(source)
    session.commit()
    session.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: UUID, session: Session = Depends(get_session)):
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    session.delete(source)
    session.commit()
    return None
