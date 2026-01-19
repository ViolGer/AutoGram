import asyncio
from sqlmodel import Session, select

from app.db.deps import engine
from app.models import Source
from app.services.html_parser import parse_html_sources
from app.services.telegram_parser import parse_telegram_sources_async


def ensure_sources(session: Session) -> None:
    # Поставь сюда страницу ProArendu, которую реально парсит html_parser (где много <a href>)
    proarendu_url = "https://proarendu.com"  # позже заменим на конкретную страницу, если added=0
    tg_url = "https://t.me/ui_jedi"

    if not session.exec(select(Source).where(Source.name == "ProArendu")).first():
        session.add(Source(type="html", name="ProArendu", url=proarendu_url, enabled=True))

    if not session.exec(select(Source).where(Source.name == "UIJedi")).first():
        session.add(Source(type="telegram", name="UIJedi", url=tg_url, enabled=True))

    session.commit()


def main() -> None:
    with Session(engine) as session:
        ensure_sources(session)
        r1 = parse_html_sources(session)
        print("HTML:", r1)

    with Session(engine) as session:
        r2 = asyncio.run(parse_telegram_sources_async(session, limit_per_channel=50))
        print("TG:", r2)


if __name__ == "__main__":
    main()
