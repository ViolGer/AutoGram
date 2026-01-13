from fastapi import APIRouter

from app.api.sources import router as sources_router
from app.api.keywords import router as keywords_router

api_router = APIRouter()
api_router.include_router(sources_router)
api_router.include_router(keywords_router)

