from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.poll import PollOut, PollWithOptions
from app.schemas.vote import VoteCreate, VoteOut, PollResults
from app.services.poll_service import PollService
from app.services.vote_service import VoteService

router = APIRouter(prefix="/polls", tags=["Polls"])


@router.get("", response_model=list[PollOut])
def list_active_polls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PollService(db).get_active_polls()


@router.get("/{poll_id}", response_model=PollWithOptions)
def get_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PollService(db).get_poll_with_options(poll_id)


@router.post("/{poll_id}/vote", response_model=VoteOut, status_code=201)
def cast_vote(
    poll_id: int,
    payload: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return VoteService(db).cast_vote(current_user.id, poll_id, payload)


@router.get("/{poll_id}/results", response_model=PollResults)
def get_results(
    poll_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return VoteService(db).get_results(poll_id)
