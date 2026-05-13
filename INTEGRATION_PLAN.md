# CatobiGato Integration Plan

## Overall Status

| Step | Status | Notes |
|------|--------|-------|
| Architecture switch: Django → FastAPI | ✅ Done | `backend-fastapi/` created, imports verified |
| Database: catobigato role + tables | ✅ Done | Existing Django tables mapped via SQLAlchemy |
| FastAPI bootstrap + Accounts + Calculator | ✅ Done | Running on port 8001 |
| Phase 2: Learning Module | 🔲 Pending | Notes, Questions, QuestionSets CRUD |
| Phase 3: Puzzles + Social | 🔲 Pending | |
| Phase 4: VisualMath (GeoGebra + Vision Pipeline) | 🔲 Pending | |
| Phase 5: MathAnimator | 🔲 Pending | |
| Phase 6: CoWriter | 🔲 Pending | |
| Phase 7: Multi-user Admin | 🔲 Pending | |

---

## Architecture Decision: FastAPI over Django

**Why FastAPI:**
- Native async — critical for LLM/AI pipelines (VisionSolverAgent, MathAnimator need async LLM calls)
- Pydantic for request/response validation (better than Django REST Framework)
- OpenAPI/Swagger built-in, better developer experience
- Modern type system, aligns with CatobiGato's AL/LLM-native goals
- No Django legacy baggage

**What's preserved:**
- PostgreSQL database (same tables, same data)
- Keycloak JWT auth (same tokens, same issuer)
- Frontend React/Vite (no changes needed there)

**What changes:**
- Django REST Framework → FastAPI + SQLAlchemy async + Pydantic
- Same business logic, same models, new framework surface

---

## Database: catobigato Role + Existing Tables

**DB:** PostgreSQL 17 at `localhost:5432`, database `catobigato`
**Role:** `catobigato` / `CatoBigato2026!` (dedicated role, table owner)
**Connection:** `postgresql+asyncpg://catobigato:CatoBigato2026!@localhost:5432/catobigato`

All existing tables are Django-created (from earlier session). SQLAlchemy models
are mapped to the actual table names and column names exactly.

---

## Project Structure

```
backend-fastapi/
  main.py                         ← FastAPI entry point (port 8001)
  requirements.txt
  .env                            ← Environment variables
  .pgpass                        ← pgpass for catobigato role
  app/
    __init__.py
    config.py                     ← Settings from environment (Pydantic)
    database.py                   ← SQLAlchemy async engine + session
    dependencies.py               ← Keycloak JWT auth, get_current_user
    models/
      accounts.py                 ← UserProfile, UserFollow (→ user_profiles, user_follows)
      calculator.py               ← CustomFunction, CalculationHistory
      learning.py                 ← Note, Question, QuestionSet
      puzzles.py                  ← PuzzleSource, Puzzle
      social.py                   ← Conversation, Message, Group
    schemas/
      accounts.py, calculator.py (TODO)
    routers/
      accounts.py                 ← GET /me, PUT /me, follow/unfollow
      calculator.py               ← POST /calculate, functions CRUD, history
    services/
      calculator_engine.py        ← SymPy engine (port from Django)
```

---

## Running the FastAPI Server

```bash
cd /home/whereq/github/catobigato.com/backend-fastapi
source venv/bin/activate

# Start server (port 8001 — port 8000 occupied by flowdesk-api)
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Or with the env file
DEBUG=true uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## API Endpoints (Phase 1)

### Accounts
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/accounts/me` | Get own profile (Keycloak JWT required) |
| PUT | `/api/v1/accounts/me` | Update own profile |
| GET | `/api/v1/accounts/profile/{user_id}` | Get public profile |
| POST | `/api/v1/accounts/follow/{user_id}` | Follow a user |
| DELETE | `/api/v1/accounts/follow/{user_id}` | Unfollow a user |
| GET | `/api/v1/accounts/followers/` | List my followers |
| GET | `/api/v1/accounts/following/` | List who I follow |

### Calculator
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/calculator/evaluate/` | Evaluate expression (mode: basic/algebra/calculus/graph) |
| GET | `/api/v1/calculator/history/` | Get calculation history |
| DELETE | `/api/v1/calculator/history/` | Clear history |
| GET | `/api/v1/calculator/functions/` | List custom functions |
| POST | `/api/v1/calculator/functions/` | Create custom function |
| DELETE | `/api/v1/calculator/functions/{id}` | Delete function |

---

## Phase 2 Plan: Learning Module

**Goal:** Notes block editor, Question Sets, Exams

### Steps
- [ ] Notes CRUD router (`app/routers/learning.py`)
- [ ] Question/QuestionSet CRUD router
- [ ] Exam + ExamAttempt models (if needed)
- [ ] Frontend: NotesPage + NoteEditor component

### Status: NOT STARTED

---

## Implementation Notes

- DeepTutor fork: `/home/whereq/github/DeepTutor` (pinned, watch for upstream changes)
- CatobiGato backend: `/home/whereq/github/catobigato.com/backend/` (Django — archived)
- CatobiGato frontend: `/home/whereq/github/catobigato.com/frontend/`
- Keycloak realm: `catobigato` at `keytomarvel.com`
- DB: PostgreSQL 17 at `localhost:5432`, database `catobigato`
- FastAPI runs on port **8001** (8000 occupied by flowdesk-api)