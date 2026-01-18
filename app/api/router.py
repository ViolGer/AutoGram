from fastapi import APIRouter

from app.api.sources import router as sources_router
from app.api.keywords import router as keywords_router
from app.api.parse import router as parse_router
from app.api.newitems import router as newitems_router
from app.api.posts import router as posts_router


api_router = APIRouter()
api_router.include_router(sources_router)
api_router.include_router(keywords_router)
api_router.include_router(parse_router)
api_router.include_router(newitems_router)
api_router.include_router(posts_router)
