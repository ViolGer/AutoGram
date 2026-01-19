import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class NewItemKeywordLink(SQLModel, table=True):
    __tablename__ = "newitem_keyword_link"

    newitem_id: uuid.UUID = Field(foreign_key="newitem.id", primary_key=True)
    keyword_id: uuid.UUID = Field(foreign_key="keyword.id", primary_key=True)


class NewItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    url: Optional[str] = None
    summary: str
    source: str
    published_at: datetime
    raw_text: Optional[str] = None

    keywords: List["Keyword"] = Relationship(
        back_populates="newitems",
        link_model=NewItemKeywordLink,
    )


class Keyword(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    word: str = Field(index=True, unique=True)

    newitems: List["NewItem"] = Relationship(
        back_populates="keywords",
        link_model=NewItemKeywordLink,
    )


class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    news_id: uuid.UUID = Field(foreign_key="newitem.id", index=True)
    generated_text: str
    published_at: datetime
    status: str = "new"


class Source(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: str
    name: str
    url: str
    enabled: bool = True


class NewItemRead(SQLModel):
    id: uuid.UUID
    title: str
    url: Optional[str] = None
    summary: str
    source: str
    published_at: datetime
    raw_text: Optional[str] = None
    keywords: list[str] = []



class PostRead(SQLModel):
    id: uuid.UUID
    news_id: uuid.UUID
    generated_text: str
    published_at: datetime
    status: str


class NewItemKeywordsUpdate(SQLModel):
    keywords: list[str] = []