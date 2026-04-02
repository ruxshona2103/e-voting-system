from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.poll import Poll
from app.repositories.base import BaseRepository


class PollRepository(BaseRepository[Poll]):
    def __init__(self, db: Session):
        super().__init__(Poll, db)

    def get_active_polls(self) -> list[Poll]:
        now = datetime.utcnow()
        return (
            self.db.query(Poll)
            .filter(
                Poll.status == "active",
                Poll.start_date <= now,
                Poll.end_date >= now,
            )
            .all()
        )

    def get_with_options(self, poll_id: int) -> Poll | None:
        return (
            self.db.query(Poll)
            .options(joinedload(Poll.options))
            .filter(Poll.id == poll_id)
            .first()
        )
