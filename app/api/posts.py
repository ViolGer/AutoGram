import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_
from sqlalchemy import func

from app.db.deps import get_session
from app.models import NewItem, Post, PostRead, Keyword, NewItemKeywordLink
from app.ai.generator import generate_post_for_item
from app.api.schemas import PostGenerateBatchRequest, PostGenerateBatchResponse, PostGenerateBatchItem


router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/generate_batch", response_model=PostGenerateBatchResponse)
def generate_posts_batch(
    payload: PostGenerateBatchRequest,
    session: Session = Depends(get_session),
):
    # 1) строим базовый select как в /newitems/search
    stmt = select(NewItem)

    if payload.source_name:
        stmt = stmt.where(NewItem.source == payload.source_name)

    if payload.query_text:
        pattern = f"%{payload.query_text}%"
        stmt = stmt.where(
            or_(
                NewItem.title.like(pattern),
                NewItem.summary.like(pattern),
                NewItem.raw_text.like(pattern),
            )
        )

    cleaned = [k.strip() for k in (payload.keywords or []) if k and k.strip()]
    cleaned_unique = list(dict.fromkeys(cleaned))

    if cleaned_unique:
        base = (
            stmt
            .join(NewItemKeywordLink, NewItemKeywordLink.newitem_id == NewItem.id)
            .join(Keyword, Keyword.id == NewItemKeywordLink.keyword_id)
            .where(Keyword.word.in_(cleaned_unique))
        )

        if payload.match_all:
            stmt = (
                base
                .group_by(NewItem.id)
                .having(func.count(func.distinct(Keyword.word)) == len(cleaned_unique))
            )
        else:
            stmt = base.distinct()

    stmt = stmt.order_by(NewItem.published_at.desc()).limit(payload.limit)

    items = session.exec(stmt).all()

    # 2) генерируем и сохраняем
    out_items: list[PostGenerateBatchItem] = []
    generated = skipped = errors = 0

    for it in items:
        try:
            # уже есть пост?
            existing = session.exec(
                select(Post).where(Post.news_id == it.id).order_by(Post.published_at.desc())
            ).first()

            if existing and payload.skip_existing and not payload.force:
                skipped += 1
                out_items.append(
                    PostGenerateBatchItem(news_id=it.id, post_id=existing.id, status="skipped")
                )
                continue

            text = generate_post_for_item(it)

            if payload.dry_run:
                generated += 1
                out_items.append(
                    PostGenerateBatchItem(news_id=it.id, status="preview", generated_text=text)
                )
                continue

            post = Post(
                news_id=it.id,
                generated_text=text,
                published_at=datetime.utcnow(),
                status="generated",
            )
            session.add(post)
            session.commit()
            session.refresh(post)

            generated += 1
            out_items.append(
                PostGenerateBatchItem(news_id=it.id, post_id=post.id, status="generated")
            )

        except Exception as e:
            session.rollback()
            errors += 1
            out_items.append(
                PostGenerateBatchItem(news_id=it.id, status="error", error=str(e))
            )

    return PostGenerateBatchResponse(
        selected=len(items),
        generated=generated,
        skipped=skipped,
        errors=errors,
        items=out_items,
    )



@router.get("/", response_model=list[PostRead])
def list_posts(
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    posts = session.exec(select(Post).order_by(Post.published_at.desc()).limit(limit)).all()
    return posts


@router.post("/generate", response_model=PostRead)
def generate_post(
    news_id: uuid.UUID = Query(..., description="ID NewItem"),
    force: bool = Query(False, description="Если true — генерируем заново даже если пост уже есть"),
    session: Session = Depends(get_session),
):
    item = session.get(NewItem, news_id)
    if not item:
        raise HTTPException(status_code=404, detail="NewItem not found")

    if not force:
        existing = session.exec(
            select(Post).where(Post.news_id == news_id).order_by(Post.published_at.desc())
        ).first()
        if existing:
            return existing

    text = generate_post_for_item(item)

    post = Post(
        news_id=news_id,
        generated_text=text,
        published_at=datetime.utcnow(),
        status="generated",
    )
    session.add(post)
    session.commit()
    session.refresh(post)
    return post
