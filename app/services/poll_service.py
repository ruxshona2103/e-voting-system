from sqlalchemy.orm import Session

from app.models.poll import Poll
from app.models.option import Option
from app.repositories.poll_repository import PollRepository
from app.repositories.option_repository import OptionRepository
from app.schemas.poll import PollCreate, PollUpdate
from app.core.exceptions import not_found, conflict, bad_request


class PollService:
    def __init__(self, db: Session):
        self.poll_repo = PollRepository(db)
        self.option_repo = OptionRepository(db)
        self.db = db

    def get_active_polls(self) -> list[Poll]:
        return self.poll_repo.get_active_polls()

    def get_poll_with_options(self, poll_id: int) -> Poll:
        poll = self.poll_repo.get_with_options(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        return poll

    def create_poll(self, data: PollCreate, creator_id: int) -> Poll:
        if data.start_date >= data.end_date:
            raise bad_request("start_date end_date dan kichik bo'lishi kerak")
        if len(data.options) < 2:
            raise bad_request("Kamida 2 ta variant bo'lishi shart")

        poll = self.poll_repo.create(
            {
                "title": data.title,
                "description": data.description,
                "start_date": data.start_date,
                "end_date": data.end_date,
                "status": "draft",
                "created_by": creator_id,
            }
        )

        for text in data.options:
            self.option_repo.create({"poll_id": poll.id, "text": text, "vote_count": 0})

        return self.poll_repo.get_with_options(poll.id)

    def update_poll(self, poll_id: int, data: PollUpdate) -> Poll:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "draft":
            raise conflict("Faqat 'draft' holatdagi so'rovnomani tahrirlash mumkin")

        update_data = data.model_dump(exclude_none=True)
        if "start_date" in update_data and "end_date" in update_data:
            if update_data["start_date"] >= update_data["end_date"]:
                raise bad_request("start_date end_date dan kichik bo'lishi kerak")

        return self.poll_repo.update(poll, update_data)

    def delete_poll(self, poll_id: int) -> None:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "draft":
            raise conflict("Faqat 'draft' holatdagi so'rovnomani o'chirish mumkin")
        self.poll_repo.delete(poll_id)

    def start_poll(self, poll_id: int) -> Poll:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "draft":
            raise conflict("Faqat 'draft' holatdagi so'rovnomani boshlash mumkin")
        return self.poll_repo.update(poll, {"status": "active"})

    def stop_poll(self, poll_id: int) -> Poll:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "active":
            raise conflict("Faqat 'active' holatdagi so'rovnomani to'xtatish mumkin")
        return self.poll_repo.update(poll, {"status": "closed"})

    def add_option(self, poll_id: int, text: str) -> Option:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "draft":
            raise conflict("Faqat 'draft' holatdagi so'rovnomaga variant qo'shish mumkin")
        return self.option_repo.create({"poll_id": poll_id, "text": text, "vote_count": 0})

    def delete_option(self, poll_id: int, option_id: int) -> None:
        poll = self.poll_repo.get(poll_id)
        if not poll:
            raise not_found("So'rovnoma topilmadi")
        if poll.status != "draft":
            raise conflict("Faqat 'draft' holatdagi so'rovnomadan variant o'chirish mumkin")
        option = self.option_repo.get(option_id)
        if not option or option.poll_id != poll_id:
            raise not_found("Variant topilmadi")
        self.option_repo.delete(option_id)
