from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.database import Base, engine
from app import models

app = FastAPI(
    title="E-Voting System API",
    version="1.0.0",
    description="Onlayn ovoz berish uchun API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_create_tables() -> None:
    _ = models
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix="/api")


