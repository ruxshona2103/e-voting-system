from pydantic import BaseModel
from datetime import datetime


class VoteCreate(BaseModel):
    option_id: int


class VoteOut(BaseModel):
    id: int
    user_id: int
    poll_id: int
    option_id: int
    voted_at: datetime

    model_config = {"from_attributes": True}


class OptionResult(BaseModel):
    option_id: int
    text: str
    vote_count: int
    percentage: float


class PollResults(BaseModel):
    poll_id: int
    total_votes: int
    results: list[OptionResult]
