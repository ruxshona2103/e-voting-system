from sqlalchemy.orm import Session

from app.models.vote import Vote
from app.models.option import Option
from app.repositories.base import BaseRepository
from app.schemas.vote import OptionResult


class VoteRepository(BaseRepository[Vote]):
    def __init__(self, db: Session):
        super().__init__(Vote, db)

    def has_voted(self, user_id: int, poll_id: int) -> bool:
        return (
            self.db.query(Vote)
            .filter(Vote.user_id == user_id, Vote.poll_id == poll_id)
            .first()
        ) is not None

    def get_results(self, poll_id: int) -> list[OptionResult]:
        options = self.db.query(Option).filter(Option.poll_id == poll_id).all()
        total = sum(o.vote_count for o in options)

        results = []
        for option in options:
            percentage = (option.vote_count / total * 100) if total > 0 else 0.0
            results.append(
                OptionResult(
                    option_id=option.id,
                    text=option.text,
                    vote_count=option.vote_count,
                    percentage=round(percentage, 2),
                )
            )
        return results
