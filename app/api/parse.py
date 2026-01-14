from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.deps import get_session
from app.services.html_parser import parse_html_sources

router = APIRouter(prefix="/api/parse", tags=["parse"])


@router.post("/html")
def parse_html(session: Session = Depends(get_session)):
    return parse_html_sources(session)
