from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.models.poll import Poll
from app.models.vote import Vote
from app.schemas.vote import PollResults
from app.services.vote_service import VoteService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("")
def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    total_users = db.query(User).count()
    total_polls = db.query(Poll).count()
    active_polls = db.query(Poll).filter(Poll.status == "active").count()
    total_votes = db.query(Vote).count()

    return {
        "total_users": total_users,
        "total_polls": total_polls,
        "active_polls": active_polls,
        "total_votes": total_votes,
    }


@router.get("/{poll_id}", response_model=PollResults)
def get_poll_stats(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return VoteService(db).get_results(poll_id)
