import uuid
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# ---------- Sources ----------
class SourceCreate(BaseModel):
    type: str  # "site" / "tg"
    name: str
    url: str
    enabled: bool = True


class SourceUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    name: str
    url: str
    enabled: bool


# ---------- Keywords ----------
class KeywordCreate(BaseModel):
    word: str


class KeywordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    word: str


class PostGenerateBatchRequest(BaseModel):
    query_text: Optional[str] = None
    source_name: Optional[str] = None
    keywords: list[str] = [Field(default_factory=list)]
    match_all: bool = False

    # поведение batch
    limit: int = 20
    skip_existing: bool = True
    force: bool = False
    dry_run: bool = False


class PostGenerateBatchItem(BaseModel):
    news_id: uuid.UUID
    post_id: Optional[uuid.UUID] = None
    status: str
    generated_text: Optional[str] = None
    error: Optional[str] = None


class PostGenerateBatchResponse(BaseModel):
    selected: int
    generated: int
    skipped: int
    errors: int
    items: list[PostGenerateBatchItem] = [Field(default_factory=list)]