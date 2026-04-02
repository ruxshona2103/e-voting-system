from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.poll import PollCreate, PollUpdate, PollOut, PollWithOptions
from app.schemas.option import OptionCreate, OptionOut
from app.schemas.user import UserOut
from app.services.poll_service import PollService
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/polls", response_model=PollWithOptions, status_code=status.HTTP_201_CREATED)
def create_poll(
    payload: PollCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).create_poll(payload, admin.id)


@router.put("/polls/{poll_id}", response_model=PollOut)
def update_poll(
    poll_id: int,
    payload: PollUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).update_poll(poll_id, payload)


@router.delete("/polls/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    PollService(db).delete_poll(poll_id)


@router.post("/polls/{poll_id}/start", response_model=PollOut)
def start_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).start_poll(poll_id)


@router.post("/polls/{poll_id}/stop", response_model=PollOut)
def stop_poll(
    poll_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).stop_poll(poll_id)


@router.post(
    "/polls/{poll_id}/options",
    response_model=OptionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_option(
    poll_id: int,
    payload: OptionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return PollService(db).add_option(poll_id, payload.text)


@router.delete(
    "/polls/{poll_id}/options/{option_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_option(
    poll_id: int,
    option_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    PollService(db).delete_option(poll_id, option_id)


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return UserRepository(db).get_all()
