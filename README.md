# E-Voting System

FastAPI + SQLAlchemy + PostgreSQL asosida qurilgan elektron ovoz berish tizimi.

## Hujjatlar

- [ARCHITECTURE.md](ARCHITECTURE.md) — loyiha tuzilishi, API endpointlar, DB jadvallari, kod namunalari

## Tezkor boshlash

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

## Texnologiyalar

FastAPI · SQLAlchemy 2.x · PostgreSQL · Alembic · JWT · Pydantic v2 · Docker
