from sqlmodel import SQLModel

from app.db.session import engine

import app.models

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
