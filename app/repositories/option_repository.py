from sqlalchemy.orm import Session

from app.models.option import Option
from app.repositories.base import BaseRepository


class OptionRepository(BaseRepository[Option]):
    def __init__(self, db: Session):
        super().__init__(Option, db)

    def increment_vote_count(self, option_id: int) -> None:
        self.db.query(Option).filter(Option.id == option_id).update(
            {Option.vote_count: Option.vote_count + 1}
        )
        self.db.commit()

    def get_by_poll(self, poll_id: int) -> list[Option]:
        return self.db.query(Option).filter(Option.poll_id == poll_id).all()
