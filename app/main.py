from fastapi import FastAPI

from app.api.router import api_router
from app.db.base import create_db_and_tables

app = FastAPI(title="AutoGram", version="0.0.1")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
