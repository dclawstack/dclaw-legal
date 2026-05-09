# DClaw Legal — Agent Development Guide

> **Read this file first before making any code changes.**
> This document is the source of truth for architecture, anti-patterns, and development workflow.

## App Identity

**DClaw Legal** is an AI contract review platform. It analyzes legal documents, detects risky clauses, scores risk, and provides recommendations using local or cloud LLMs.

- **Backend Port:** `8099` (FastAPI)
- **Frontend Port:** `3013` (Next.js)
- **Database:** `dclaw_legal` (PostgreSQL)
- **Base API Path:** `/api/v1`

## Architecture Lock — DO NOT CHANGE

These are non-negotiable. If an agent suggests changing them, reject it.

### Backend
- **FastAPI** with `lifespan` handler
- **SQLAlchemy 2.0** — `DeclarativeBase` from `app.models.base`, NOT `declarative_base()`
- **Pydantic v2** schemas with `ConfigDict(from_attributes=True)`
- **Async SQLAlchemy** — `create_async_engine` + `AsyncSession`
- **Repository pattern** — all DB access through `app/repositories/`
- **Dependency injection** — `Depends(get_db)`, never manual `AsyncSession`
- **NO MOCK DATA** — never use in-memory `dict`s

### Frontend
- **Next.js 14+ App Router**
- **Tailwind CSS** + vanilla HTML inputs (no shadcn/ui yet — can be added)
- **API client** in `src/lib/api.ts` — typed fetch wrapper
- **Environment variables** — `NEXT_PUBLIC_API_URL` baked at build time. Dockerfile MUST declare `ARG NEXT_PUBLIC_API_URL`.

### Docker
- **Backend:** `python:3.11-slim`, non-root `appuser`, healthcheck with `python urllib.request.urlopen()`
- **Frontend:** `node:20-alpine`, port `3013`
- **Compose:** container port MUST match `EXPOSE`/`ENV PORT`

## Directory Structure

```
dclaw-legal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py              # FastAPI factory
│   │   │   ├── routes/
│   │   │   │   └── health.py
│   │   │   └── v1/
│   │   │       └── legal.py         # Contract review router
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py          # Base(DeclarativeBase), engine, get_db
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   └── contract_review.py   # ContractReview, ClauseFinding
│   │   ├── repositories/            # CRUD layer
│   │   ├── schemas/                 # Pydantic v2
│   │   └── services/
│   │       └── legal_service.py     # AI contract analysis
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── dashboard/
│   │   │       └── page.tsx         # Contract review UI
│   │   └── lib/
│   │       └── api.ts
│   └── Dockerfile
├── docker-compose.yml
├── helm/
└── .env.example
```

## Anti-Patterns — NEVER DO

| Anti-Pattern | Why It Breaks Things | Correct Alternative |
|--------------|---------------------|---------------------|
| `declarative_base()` in `database.py` | Separate metadata → zero tables | `class Base(DeclarativeBase): pass` |
| `curl` in healthcheck on `python:*-slim` | No `curl` → silent failure | `python -c "import urllib.request; urllib.request.urlopen(...)"` |
| In-memory `MOCK_*` dicts | Data lost on restart | Create repository + real DB |
| Missing `ARG NEXT_PUBLIC_API_URL` | Wrong API URL baked in | Add `ARG NEXT_PUBLIC_API_URL` before build |
| Manual `get_db()` with `__anext__()` | Session leaks | `Depends(get_db)` |
| Hardcoded `localhost:PORT` | Breaks Docker/K8s | Use `process.env.NEXT_PUBLIC_API_URL` |
| No alembic migration for new models | Schema drift | `alembic revision --autogenerate` |
| Frontend calling mock data | UI not connected to backend | Wire API client to real endpoints |

## Database Rules

1. All models MUST inherit from `Base` in `app/models.base`
2. All models MUST use `Mapped[...]` and `mapped_column()`
3. **Never use `default_factory=` in `mapped_column()`** — use `default=` instead
3. Relationships MUST specify `lazy="selectin"`
4. All new tables MUST get an alembic migration
5. `ondelete="CASCADE"` for clause_findings (children of contract_reviews)

## How to Add a Feature

1. **Read this file** and `PLAN-v1.2.md`
2. **Backend:**
   - Add/update model in `app/models/`
   - Add/update schema in `app/schemas/`
   - Add repository in `app/repositories/`
   - Add/update router in `app/api/v1/`
   - Add tests in `tests/`
   - Generate alembic migration
3. **Frontend:**
   - Add API types/functions to `src/lib/api.ts`
   - Add page in `src/app/` or component
4. **Docker:** Verify `docker compose config` and `docker compose up -d`
5. **Commit** with conventional commit message

## Testing Requirements

- Every new router endpoint MUST have tests
- Use `pytest-asyncio` with `async` test functions
- Use `httpx.AsyncClient` with `ASGITransport`
- Override `get_db` dependency with test session

## Port Registry

| Service | Host Port | Container Port |
|---------|-----------|----------------|
| legal-frontend | 3013 | 3013 |
| legal-backend | 8099 | 8099 |
| legal-postgres | 5432 | 5432 |
