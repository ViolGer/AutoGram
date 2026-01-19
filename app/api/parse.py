from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.deps import get_session
from app.services.html_parser import parse_html_sources
from app.services.telegram_parser import parse_telegram_sources_async

router = APIRouter(prefix="/api/parse", tags=["parse"])


@router.post("/telegram")
async def parse_telegram(limit: int = 20, session: Session = Depends(get_session)):
    return await parse_telegram_sources_async(session, limit_per_channel=limit)


@router.post("/html")
def parse_html(session: Session = Depends(get_session)):
    return parse_html_sources(session)
