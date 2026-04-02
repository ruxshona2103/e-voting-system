from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    poll_id: Mapped[int] = mapped_column(
        ForeignKey("polls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    vote_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    poll = relationship("Poll", back_populates="options")
    votes = relationship("Vote", back_populates="option")

