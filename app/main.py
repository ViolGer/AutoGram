from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.db.base import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="AutoGram", version="0.0.1", lifespan=lifespan)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
