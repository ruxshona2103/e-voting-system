from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.poll_repository import PollRepository
from app.repositories.vote_repository import VoteRepository
from app.repositories.option_repository import OptionRepository
from app.models.vote import Vote
from app.schemas.vote import VoteCreate, OptionResult, PollResults
from app.core.exceptions import not_found, conflict, bad_request


class VoteService:
    def __init__(self, db: Session):
        self.poll_repo = PollRepository(db)
        self.vote_repo = VoteRepository(db)
        self.option_repo = OptionRepository(db)

    def cast_vote(self, user_id: int, poll_id: int, data: VoteCreate) -> Vote:
        # 1. Poll mavjudmi?
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")

        # 2. Poll faolmi?
        if poll.status != "active":
            raise conflict("So'rovnoma hozir faol emas")

        # 3. Sana oralig'idami?
        now = datetime.utcnow()
        if not (poll.start_date <= now <= poll.end_date):
            raise conflict("So'rovnoma vaqti o'tgan yoki hali boshlanmagan")

        # 4. Allaqachon ovoz berganmi?
        if self.vote_repo.has_voted(user_id, poll_id):
            raise conflict("Siz allaqachon bu so'rovnomaga ovoz bergansiz")

        # 5. Option shu pollga tegishlimi?
        option = self.option_repo.get(data.option_id)
        if not option or option.poll_id != poll_id:
            raise bad_request("Variant bu so'rovnomaga tegishli emas")

        # 6. Ovozni yozish
        vote = self.vote_repo.create(
            {
                "user_id": user_id,
                "poll_id": poll_id,
                "option_id": data.option_id,
            }
        )

        # 7. vote_count ni oshirish (atomik)
        self.option_repo.increment_vote_count(data.option_id)

        return vote

    def get_results(self, poll_id: int) -> PollResults:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")

        results = self.vote_repo.get_results(poll_id)
        total = sum(r.vote_count for r in results)

        return PollResults(
            poll_id=poll_id,
            total_votes=total,
            results=results,
        )
