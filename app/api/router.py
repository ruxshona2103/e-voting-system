from fastapi import APIRouter

from app.api import auth, polls, admin, stats

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(polls.router)
api_router.include_router(admin.router)
api_router.include_router(stats.router)


@api_router.get("/")
def api_root():
    return {"message": "E-Voting API is running"}
