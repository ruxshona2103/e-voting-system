# ARCHITECTURE — E-Voting System

> Bu hujjat loyihaga kirgan har qanday dasturchi yoki agent uchun yozilgan.
> Shu faylni o'qib, tizimning barcha qismini, logikasini va qoidalarini to'liq tushunib olish mumkin.

---

## 1. Tizim nima qiladi?

Elektron ovoz berish veb-tizimi. Foydalanuvchilar ro'yxatdan o'tib, faol so'rovnomalarga ovoz beradi. Administrator so'rovnomalarni boshqaradi. Tizim har bir foydalanuvchi faqat bir marta ovoz berishini kafolatlaydi.

**Asosiy aktorlar:**

| Rol | Imkoniyatlari |
|-----|---------------|
| `user` | Ro'yxatdan o'tish, kirish, ovoz berish, natijalarni ko'rish |
| `admin` | Yuqoridagilarga qo'shimcha: so'rovnoma yaratish/tahrirlash/boshqarish, foydalanuvchilar ro'yxati, statistika |

---

## 2. Texnologiyalar

| Komponent | Texnologiya | Versiya |
|-----------|------------|---------|
| Backend framework | FastAPI | 0.115+ |
| ORM | SQLAlchemy | 2.x |
| Ma'lumotlar bazasi | PostgreSQL | 15 |
| Migratsiya | Alembic | 1.13+ |
| Auth | JWT (python-jose) + bcrypt (passlib) | — |
| Validatsiya | Pydantic | v2 |
| Test | pytest + httpx | — |
| Container | Docker + docker-compose | — |

---

## 3. Arxitektura: 4-qatlam

```
┌─────────────────────────────────────────┐
│           API Layer  (app/api/)          │  ← Faqat HTTP: so'rov qabul, javob qaytarish
├─────────────────────────────────────────┤
│        Service Layer  (app/services/)    │  ← Biznes qoidalar, validatsiya, orchestration
├─────────────────────────────────────────┤
│     Repository Layer  (app/repositories/)│  ← Faqat DB so'rovlar, SQL logic
├─────────────────────────────────────────┤
│         Database  (PostgreSQL)           │  ← Ma'lumot saqlash
└─────────────────────────────────────────┘
```

**Qat'iy qoida:** Har bir qatlam faqat o'zidan pastki qatlamni chaqiradi.
API → Service → Repository → DB. Orqaga yoki o'tib ketish yo'q.

---

## 4. Fayl Tuzilishi

```
e-voting-system/
│
├── app/
│   ├── main.py                   # FastAPI app, CORS, router ulash
│   ├── config.py                 # Barcha env o'zgaruvchilar (Pydantic Settings)
│   ├── database.py               # SQLAlchemy engine, SessionLocal, Base
│   │
│   ├── core/
│   │   ├── security.py           # bcrypt hash, JWT yaratish/decode
│   │   ├── dependencies.py       # get_db, get_current_user, require_admin
│   │   └── exceptions.py         # Custom HTTP xatoliklar (404, 403, 409...)
│   │
│   ├── models/                   # SQLAlchemy ORM — DB jadvallari
│   │   ├── user.py
│   │   ├── poll.py
│   │   ├── option.py
│   │   └── vote.py
│   │
│   ├── schemas/                  # Pydantic — request/response shakllari
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── poll.py
│   │   ├── option.py
│   │   └── vote.py
│   │
│   ├── repositories/             # DB bilan muloqot (faqat SQL)
│   │   ├── base.py               # BaseRepository[T] — umumiy CRUD
│   │   ├── user_repository.py
│   │   ├── poll_repository.py
│   │   ├── option_repository.py
│   │   └── vote_repository.py
│   │
│   ├── services/                 # Biznes logika
│   │   ├── auth_service.py
│   │   ├── poll_service.py
│   │   └── vote_service.py
│   │
│   └── api/                      # HTTP endpoint'lar
│       ├── router.py             # Barcha routerlarni birlashtiradi
│       ├── auth.py               # /api/auth/*
│       ├── polls.py              # /api/polls/*
│       ├── admin.py              # /api/admin/*
│       └── stats.py              # /api/stats/*
│
├── alembic/
│   ├── versions/                 # Migration fayllar
│   └── env.py
│
├── tests/
│   ├── conftest.py               # DB fixture, test client, token helper
│   ├── test_auth.py
│   ├── test_polls.py
│   └── test_votes.py
│
├── .env.example
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 5. Ma'lumotlar Bazasi

### 5.1 Jadvallar va maydonlar

**users**
```
id          SERIAL PRIMARY KEY
name        VARCHAR(100)   NOT NULL
email       VARCHAR(255)   NOT NULL UNIQUE
password    VARCHAR(255)   NOT NULL          -- bcrypt hash, hech qachon plain text emas
role        VARCHAR(10)    NOT NULL DEFAULT 'user'  -- 'user' | 'admin'
created_at  TIMESTAMP      NOT NULL DEFAULT now()
```

**polls**
```
id           SERIAL PRIMARY KEY
title        VARCHAR(255)  NOT NULL
description  TEXT
start_date   TIMESTAMP     NOT NULL
end_date     TIMESTAMP     NOT NULL
status       VARCHAR(10)   NOT NULL DEFAULT 'draft'  -- 'draft' | 'active' | 'closed'
created_by   INTEGER       NOT NULL REFERENCES users(id)
created_at   TIMESTAMP     NOT NULL DEFAULT now()
```

**options**
```
id          SERIAL PRIMARY KEY
poll_id     INTEGER        NOT NULL REFERENCES polls(id) ON DELETE CASCADE
text        VARCHAR(255)   NOT NULL
vote_count  INTEGER        NOT NULL DEFAULT 0   -- denormalized, tez hisob uchun
```

**votes**
```
id          SERIAL PRIMARY KEY
user_id     INTEGER        NOT NULL REFERENCES users(id)
poll_id     INTEGER        NOT NULL REFERENCES polls(id)
option_id   INTEGER        NOT NULL REFERENCES options(id)
voted_at    TIMESTAMP      NOT NULL DEFAULT now()

UNIQUE (user_id, poll_id)   -- ← BU ENG MUHIM CONSTRAINT: qayta ovoz berish imkonsiz
```

### 5.2 Jadvallar o'rtasidagi aloqalar

```
users ──< votes >── polls
              │
           options
polls ──< options
```

- Bir `user` ko'p `vote` bera oladi, lekin har bir `poll` ga faqat bittasini
- Bir `poll` da ko'p `option` bo'ladi
- Har bir `vote` aniq bitta `option` ga bog'langan

### 5.3 `vote_count` nima uchun denormalized?

`options.vote_count` har safar `SELECT COUNT(*)` qilmaslik uchun mavjud.
Ovoz berilganda `UPDATE options SET vote_count = vote_count + 1` atomik bajariladi.
Natijalar sahifasi bu ustunni to'g'ridan o'qiydi — tezroq.

---

## 6. Auth Tizimi

### Token strategiyasi

```
Login → access_token (30 daqiqa) + refresh_token (7 kun)
```

- `access_token`: har so'rovda `Authorization: Bearer <token>` sarlavhasida yuboriladi
- `refresh_token`: muddati tugaganda yangi access_token olish uchun ishlatiladi
- Ikkalasi ham JWT (HS256), `SECRET_KEY` bilan imzolangan

### Parol xavfsizligi

- Parol hech qachon ochiq saqlanmaydi
- `passlib[bcrypt]` kutubxonasi ishlatiladi
- Ro'yxatda: `get_password_hash(password)` → DB ga yoziladi
- Kirishda: `verify_password(plain, hashed)` → solishtirish

### Rol tekshiruvi

```python
# dependencies.py da
get_current_user()  # JWT dan user_id oladi, DB dan user ni qaytaradi
require_admin()     # get_current_user() + role == 'admin' tekshiruvi, aks holda 403
```

---

## 7. API Endpointlar

Barcha so'rovlar `/api` prefiksi bilan boshlanadi.

### Auth  (token talab qilinmaydi)
```
POST  /api/auth/register    Yangi foydalanuvchi yaratish
POST  /api/auth/login       Email+parol → access+refresh token
POST  /api/auth/refresh     Refresh token → yangi access token
```

### Polls  (login: Bearer token kerak)
```
GET   /api/polls               Faol (active) so'rovnomalar ro'yxati
GET   /api/polls/{id}          Bitta so'rovnoma + variantlar
POST  /api/polls/{id}/vote     Ovoz berish  → body: { "option_id": N }
GET   /api/polls/{id}/results  Natijalar: har variant uchun foiz + ovoz soni
```

### Admin  (login + admin roli kerak)
```
POST    /api/admin/polls                      Yangi so'rovnoma yaratish
PUT     /api/admin/polls/{id}                 Tahrirlash (faqat draft holatida)
DELETE  /api/admin/polls/{id}                 O'chirish (faqat draft holatida)
POST    /api/admin/polls/{id}/start           Statusni active ga o'tkazish
POST    /api/admin/polls/{id}/stop            Statusni closed ga o'tkazish
POST    /api/admin/polls/{id}/options         Variant qo'shish
DELETE  /api/admin/polls/{id}/options/{oid}   Variant o'chirish
GET     /api/admin/users                      Barcha foydalanuvchilar ro'yxati
```

### Stats  (login + admin roli kerak)
```
GET   /api/stats              Tizim bo'yicha umumiy statistika
GET   /api/stats/{poll_id}    Bitta so'rovnoma statistikasi (PDF eksport ham shu yerda)
```

---

## 8. Biznes Qoidalari (Service Layer)

### 8.1 `auth_service.py`

**register:**
1. Email allaqachon mavjudmi? → `409 Conflict`
2. Parolni hash qil
3. User yarat (`role='user'` default)
4. access + refresh token qaytarish

**login:**
1. Email bo'yicha user topilmadimi? → `401 Unauthorized`
2. `verify_password` muvaffaqiyatsizmi? → `401 Unauthorized`
3. access + refresh token qaytarish

### 8.2 `poll_service.py`

**create_poll:**
- `start_date < end_date` tekshiruvi → `400 Bad Request`
- Kamida 2 ta option bo'lishi shart → `400 Bad Request`
- Yaratilganda `status = 'draft'`

**start_poll:**
- Hozirgi holat `draft` emas? → `409 Conflict`
- `status = 'active'` ga o'tkazish

**stop_poll:**
- Hozirgi holat `active` emas? → `409 Conflict`
- `status = 'closed'` ga o'tkazish

**update/delete:**
- Faqat `draft` holatdagi poll o'zgartiriladi
- `active` yoki `closed` poll tahrirlanmaydi → `409 Conflict`

### 8.3 `vote_service.py`

**cast_vote — eng muhim biznes logika:**
```
1. Poll topilmadimi?                          → 404 Not Found
2. Poll.status == 'active' emasmi?            → 409 Conflict  ("so'rovnoma faol emas")
3. Hozirgi vaqt start_date..end_date oralig'idami? → 409 Conflict
4. has_voted(user_id, poll_id) == True?       → 409 Conflict  ("allaqachon ovoz bergansiz")
5. option_id poll ga tegishlimi?              → 400 Bad Request
6. Vote DB ga yoziladi
7. options.vote_count += 1  (atomik UPDATE)
```

---

## 9. Repository Qatlami

### BaseRepository[T] — umumiy CRUD

```python
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session): ...

    def get(self, id: int) -> ModelType | None
    def get_all(self) -> list[ModelType]
    def create(self, obj_in: dict) -> ModelType
    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType
    def delete(self, id: int) -> None
```

### Maxsus metodlar

**UserRepository**
```python
get_by_email(email: str) -> User | None
```

**PollRepository**
```python
get_active_polls() -> list[Poll]       # status='active' va sana chegarasi ichida
get_with_options(poll_id: int) -> Poll # options bilan birga (joinedload)
```

**VoteRepository**
```python
has_voted(user_id: int, poll_id: int) -> bool
get_results(poll_id: int) -> list[OptionResult]  # har variant uchun count + foiz
```

**OptionRepository**
```python
increment_vote_count(option_id: int) -> None  # atomik UPDATE ... SET vote_count += 1
```

---

## 10. Asosiy Fayllar Kodi (Skelet)

### app/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()
```

### app/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
```

### app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(title="E-Voting System", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(api_router, prefix="/api")
```

### app/api/router.py
```python
from fastapi import APIRouter
from app.api import auth, polls, admin, stats

api_router = APIRouter()
api_router.include_router(auth.router,  prefix="/auth",  tags=["Auth"])
api_router.include_router(polls.router, prefix="/polls", tags=["Polls"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
```

### app/core/dependencies.py
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository

bearer = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token=Depends(bearer), db=Depends(get_db)):
    payload = decode_token(token.credentials)  # invalid → 401
    user = UserRepository(db).get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user

def require_admin(user=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin huquqi talab etiladi")
    return user
```

---

## 11. HTTP Xatolik Kodlari

| Kod | Holat |
|-----|-------|
| `400` | Noto'g'ri so'rov (sana xato, option boshqa poll ga tegishli...) |
| `401` | Token yo'q, noto'g'ri yoki muddati o'tgan |
| `403` | Token bor, lekin ruxsat yo'q (admin kerak) |
| `404` | Poll yoki user topilmadi |
| `409` | Mantiqiy ziddiyat (allaqachon ovoz bergan, poll faol emas, email band...) |
| `422` | Pydantic validatsiya xatosi (FastAPI avtomatik) |

---

## 12. SOLID Qoidalari Qanday Qo'llanilgan

| Princip | Izoh |
|---------|------|
| **S** — Single Responsibility | `api/` faqat HTTP, `services/` faqat logika, `repositories/` faqat SQL |
| **O** — Open/Closed | `BaseRepository` o'zgartirilmasdan, meros orqali kengaytiriladi |
| **L** — Liskov | Har bir `XRepository(BaseRepository)` asosiy metodlarni buzmasdan override qiladi |
| **I** — Interface Segregation | `VoteService` faqat `VoteRepository` va `PollRepository` ni oladi, boshqasini emas |
| **D** — Dependency Inversion | `Service` → `Repository` interfeysiga bog'liq, to'g'ridan `db.query()` chaqirmaydi |

---

## 13. Muhit O'zgaruvchilari (.env)

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/evoting_db
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 14. Docker

### docker-compose.yml
```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: evoting_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    env_file: .env
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

---

## 15. Requirements

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.36
alembic==1.13.3
psycopg2-binary==2.9.9
pydantic==2.9.2
pydantic-settings==2.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pytest==8.3.3
httpx==0.27.2
```

---

## 16. Loyihani Ishga Tushirish

```bash
# 1. Virtual muhit
python -m venv venv && source venv/bin/activate

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. .env sozla
cp .env.example .env

# 4. DB migratsiyalari
alembic upgrade head

# 5. Serverni ishga tushir
uvicorn app.main:app --reload

# Swagger UI → http://localhost:8000/docs
# ReDoc      → http://localhost:8000/redoc
```

---

## 17. Test Yozish Tartibi

```bash
# Barcha testlar
pytest tests/ -v

# Bitta modul
pytest tests/test_votes.py -v
```

`conftest.py` da:
- `test_db` fixture — har test uchun alohida tranzaksiya, rollback bilan
- `test_client` — `httpx.AsyncClient` + `override_dependencies` (real DB, mock emas)
- `user_token` / `admin_token` — tayyor JWT tokenlar

---

## 18. Qo'shimcha Texnik Topshiriq (TT)

Quyidagi TT loyihaning funksional va nofunksional talablarini kengaytiruvchi rasmiy talablar to'plami sifatida qabul qilinadi.

### 18.1 Umumiy ma'lumotlar
- **Loyiha nomi:** Elektron ovoz berish axborot tizimi
- **Maqsad:** Onlayn ovoz berish jarayonini tashkil etish, ovozlarni avtomatik hisoblash, natijalarni real vaqt rejimida ko'rsatish
- **Qo'llanish sohasi:** O'quv loyihasi / kurs ishi / ichki korxona tizimi

### 18.2 Tizim vazifasi
- Elektron ovoz berishni tashkil etish
- Ovozlarni avtomatik hisoblash
- Natijalarni jadval va diagrammada chiqarish
- Administrator orqali jarayonni boshqarish

### 18.3 Funktsional talablar

#### Foydalanuvchi funktsiyalari
1. Ro'yxatdan o'tish
2. Tizimga kirish (avtorizatsiya)
3. Faol ovoz berishlarni ko'rish
4. Variant tanlash
5. Ovoz berish
6. Natijalarni ko'rish
7. Tizimdan chiqish

#### Administrator funktsiyalari
1. Yangi ovoz berish yaratish
2. Parametrlarni tahrirlash
3. Boshlanish/tugash sanalarini belgilash
4. Variantlar qo'shish
5. Ovoz berishni boshlash/to'xtatish
6. Statistikani ko'rish
7. Foydalanuvchilarni boshqarish

#### Tizim funktsiyalari
1. 1 foydalanuvchi — 1 ovoz nazorati
2. Ma'lumotlarni bazada saqlash
3. Ovozlarni avtomatik hisoblash
4. Yakuniy hisobot shakllantirish
5. Natijalarni real vaqtga yaqin yangilash

### 18.4 Nofunktsional talablar

#### Ishlash tezligi
- Kamida 1000 bir vaqtning o'zida foydalanuvchini qo'llab-quvvatlash
- O'rtacha javob vaqti 3 soniyadan oshmasligi

#### Ishonchlilik
- Ma'lumot yo'qolmasligi
- Ovozlarning to'g'ri saqlanishi

#### Xavfsizlik
- Parollar hash holatda saqlanishi
- Qayta ovoz berishning oldi olinishi
- Role-based access (`user`/`admin`)
- HTTPS orqali ishlashga tayyor bo'lish

#### Interfeys
- Oddiy va tushunarli dizayn
- Mobil qurilmalarda ishlashi
- Natijalarni jadval, diagramma, foiz ko'rinishida chiqarish

### 18.5 Ma'lumotlar bazasi talablari
Asosiy jadvallar va maydonlar `users`, `polls`, `options`, `votes` bo'lib, ushbu hujjatning 5-bo'limidagi sxema TT bilan mos keladi.

### 18.6 Arxitektura talabi
- Mijoz-server, 3 pog'onali yondashuv:
  1. Mijoz (brauzer)
  2. Backend ilova serveri
  3. Ma'lumotlar bazasi serveri

### 18.7 Texnologik talablar
- **Frontend:** HTML, CSS, JavaScript (React/Vue)
- **Backend:** Node.js / Python / Java (ushbu loyihada Python + FastAPI)
- **DB:** PostgreSQL / MySQL (ushbu loyihada PostgreSQL)

### 18.8 Hisobot talablari
Tizim quyidagilarni shakllantirishi kerak:
- Umumiy ovozlar soni
- Har bir variant bo'yicha foiz
- Ovozlar taqsimoti diagrammasi
- PDF eksport imkoniyati

### 18.9 Ishlab chiqish bosqichlari
1. DB loyihalash
2. Backend dasturlash
3. Frontend dasturlash
4. Integratsiya
5. Test sinovlari
6. Ishga tushirish

### 18.10 Qabul mezonlari
Tizim tayyor deb hisoblanadi, agar:
- Foydalanuvchi ro'yxatdan o'tib ovoz bera olsa
- Ovoz to'g'ri saqlansa
- Qayta ovoz berish imkoni bo'lmasa
- Natijalar to'g'ri ko'rsatilsa
- Administrator jarayonni boshqara olsa
