from pydantic import BaseModel


class OptionOut(BaseModel):
    id: int
    poll_id: int
    text: str
    vote_count: int

    model_config = {"from_attributes": True}


class OptionCreate(BaseModel):
    text: str
