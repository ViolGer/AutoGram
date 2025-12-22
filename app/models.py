import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class NewItem(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    title: str
    url: Optional[str] = None
    summary: str
    source: str
    published_at: datetime
    raw_text: Optional[str] = None


class Post(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    news_id: uuid.UUID
    generated_text: str
    published_at: datetime
    status: str = 'new'


class Source(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    type: str
    name: str
    url: str
    enabled: bool = True


class Keyword(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    word: str
