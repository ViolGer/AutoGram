from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
