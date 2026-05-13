# CatobiGato FastAPI Migration Plan

## Why FastAPI

- Native async — better for LLM/AI agent pipelines (VisionSolverAgent, MathAnimator need async calls)
- Modern type system (Pydantic vs Django models, better OpenAPI/Swagger)
- Natural fit for CatobiGato's AL/LLM-native features
- No Django legacy baggage — cleaner service boundaries
- Same PostgreSQL database, same Keycloak auth — only the framework changes

## Scope

**Keep:** PostgreSQL DB (same tables, same data), Keycloak JWT auth (same tokens), frontend React/Vite
**Change:** Django REST Framework → FastAPI + SQLAlchemy + Pydantic

## New Project Structure

```
backend/                          ← existing Django (kept for reference, will be archived)
backend-fastapi/
  main.py                         ← FastAPI application entry point
  requirements.txt
  app/
    __init__.py
    config.py                     ← Settings from environment
    database.py                   ← SQLAlchemy engine + session
    dependencies.py               ← Auth dependencies (Keycloak JWT)
    models/                       ← SQLAlchemy models (one file per app)
      __init__.py
      accounts.py
      calculator.py
      learning.py
      puzzles.py
      social.py
      visual_math.py
    schemas/                      ← Pydantic request/response models
      __init__.py
      accounts.py
      calculator.py
      learning.py
      puzzles.py
      social.py
      visual_math.py
    routers/                      ← API route modules
      __init__.py
      accounts.py
      calculator.py
      learning.py
      puzzles.py
      social.py
      visual_math.py
    services/                     ← Business logic
      __init__.py
      geogebra_service.py
      vision_solver_agent.py
      math_animator_service.py
      cowriter_service.py
      keycloak_admin.py           ← Keycloak admin API client
    tasks/                        ← Celery tasks (Phase 3+)
      __init__.py
```

## Migration Order

### Step 0: Bootstrap FastAPI project
- [ ] Create `backend-fastapi/` directory
- [ ] Create `requirements.txt` (fastapi, uvicorn, sqlalchemy, asyncpg, pydantic, python-jose, httpx, alembic)
- [ ] Create `app/config.py` (env-loaded settings)
- [ ] Create `app/database.py` (SQLAlchemy async engine)
- [ ] Create `app/dependencies.py` (Keycloak JWT auth dependency)
- [ ] Create `main.py` (FastAPI app with all routers mounted)

### Step 1: Accounts app (auth + user profiles)
- [ ] Create `app/models/accounts.py` (UserProfile, UserFollow — mirror Django models)
- [ ] Create `app/schemas/accounts.py` (Pydantic models)
- [ ] Create `app/routers/accounts.py` (GET /me, PUT /me, POST /follow, DELETE /follow, GET /users/{id})
- [ ] Wire Keycloak JWT → SQLAlchemy user lookup
- [ ] Test: auth endpoints work with existing Keycloak tokens

### Step 2: Calculator app
- [ ] Create `app/models/calculator.py` (CustomFunction, CalculationHistory)
- [ ] Create `app/schemas/calculator.py`
- [ ] Create `app/routers/calculator.py` (POST /calculate, GET /history, POST /functions, GET /functions)
- [ ] Port CalculatorEngine from `apps/calculator/engine.py`
- [ ] Test: calculator still works end-to-end

### Step 3: Learning app
- [ ] Create models, schemas, routers for Note, Question, QuestionSet, ExamAttempt, StudyGroup, StudyGroupMembership
- [ ] Port business logic from Django views/serializers
- [ ] Test: CRUD operations work

### Step 4: Puzzles + Social apps
- [ ] Port PuzzleSource, Puzzle, Conversation, Message models

### Step 5: VisualMath app (Phase 1 stub already exists)
- [ ] Port `GeoGebraSketch` and `AnimationProject` models
- [ ] Port `VisualMathService`, `GeoGebraService`, `MathAnimatorService`
- [ ] Port existing VisualMathPage API endpoints
- [ ] Phase 2 VisionSolverAgent port (see below)

### Step 6: Phase 2 — VisionSolverAgent (Vision Pipeline)
- [ ] Port 4-stage pipeline from DeepTutor `agents/vision_solver/`
- [ ] Port ggb_validator from `tools/vision/ggb_validator.py`
- [ ] Wire into GeoGebraService as real implementation

### Step 7: Phase 3 — MathAnimator
- [ ] Port MathAnimatorPipeline from DeepTutor
- [ ] Set up Celery worker for Manim rendering

### Step 8: Phase 4 — CoWriter
- [ ] Create `app/services/cowriter_service.py`
- [ ] Port EditAgent from DeepTutor `co_writer/edit_agent.py`

### Step 9: Phase 5 — Multi-user Admin
- [ ] Create `app/services/keycloak_admin.py` (Keycloak REST API client)
- [ ] Create AdminGrant model + admin endpoints
- [ ] Admin audit logging

## Key Decisions

### Auth: Keep Keycloak JWT
FastAPI will use the same `python-jose` + Keycloak JWKS approach as Django.
`dependencies.py` provides `get_current_user()` dependency that reads the
`Authorization: Bearer <token>` header, validates against Keycloak JWKS,
and returns a `CurrentUser` Pydantic model.

### Database: Same PostgreSQL
Use `sqlalchemy.ext.asyncio` with `asyncpg` driver.
Run Django migration → keep the same tables.
Alem bic can be used for future schema management (not needed for migration).

### Models: SQLAlchemy, not ORM
Each Django `models.Model` becomes a SQLAlchemy `Table` + `mapper`.
Field names and types stay identical — same PostgreSQL tables.

### Async: Use it where it matters
API endpoints are `async def` for FastAPI.
Services that call LLMs (VisionSolverAgent, MathAnimatorService) are `async`.
Services that are pure Python (CalculatorEngine) can be sync or async.

### Multi-stage pipelines: async generators
Long-running pipelines (VisionSolverAgent, MathAnimatorPipeline) return
`AsyncGenerator[StageUpdate, None]` so the frontend can SSE-poll or stream stages.

## Verification Checklist

After each step:
- [ ] `python -m uvicorn app.main:app --reload` starts without import errors
- [ ] `GET /docs` (Swagger UI) loads
- [ ] Existing Keycloak tokens work for authenticated endpoints
- [ ] PostgreSQL tables are readable/writable
- [ ] Frontend can still call API (test one endpoint manually)

## Phase 2 DeepTutor Reference Files

- `agents/vision_solver/vision_solver_agent.py` — 4-stage pipeline
- `tools/vision/ggb_validator.py` — GGBScript validator
- `tools/prompting/hints/en/geogebra_analysis.yaml` — prompt templates
- `agents/math_animator/pipeline.py`, `renderer.py`, `models.py` — Phase 3 ref
- `co_writer/edit_agent.py` — Phase 4 ref
- `multi_user/router.py`, `grants.py`, `audit.py` — Phase 5 ref

## Timeline Summary

```
Step 0-1: Bootstrap + Accounts       (foundation)
Step 2:   Calculator + Engine         (proof of concept)
Step 3:   Learning app                (mid-size migration)
Step 4:   Puzzles + Social            (small apps)
Step 5:   VisualMath (Phase 1 stub)   (existing work moves here)
Step 6:   Phase 2 VisionSolverAgent   (LLM pipeline, the main event)
Step 7:   Phase 3 MathAnimator
Step 8:   Phase 4 CoWriter
Step 9:   Phase 5 Multi-user Admin
```