from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.schemas.option import OptionOut


class PollCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    options: list[str] = Field(min_length=2)


class PollUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class PollOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    status: str
    created_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PollWithOptions(PollOut):
    options: list[OptionOut] = []
