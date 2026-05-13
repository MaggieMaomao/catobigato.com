# CatobiGato.com — Technical Specification

**Version**: 0.1.0  
**Status**: Pre-alpha — Scaffolding  
**Last updated**: 2026-05-10

---

## 1. Architecture Overview

### Pattern: Modular Monolith
```
frontend (React/TS/Vite) ←→ backend (Django/DRF) ←→ PostgreSQL 17
                                            ↑
                                      Keycloak (Auth)
```

### Infrastructure (Existing)
| Service | Host | Port | Note |
|---|---|---|---|
| PostgreSQL | localhost | 5432 | `whereq-postgres:17` |
| Keycloak | localhost | 8888 | `whereq/keycloak-k2m:latest` |

### Environment
- Python 3.12+ / Django 6+
- Node 24+ / React 18+ / TypeScript 5+
- Yarn as package manager

---

## 2. Backend Structure

```
backend/
├── catobigato/              # Django project
│   ├── __init__.py
│   ├── settings/            # Environment-aware settings
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                   # Feature modules
│   ├── core/               # Shared (utils, middleware, decorators)
│   ├── accounts/           # User profiles, Keycloak sync
│   ├── calculator/         # Expression parser, functions, graphing
│   ├── subjects/           # Physics, Chemistry, Biology content
│   ├── learning/           # Notes, question sets, exams
│   ├── puzzles/            # Puzzle bank management
│   └── social/             # Follows, groups, messaging
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Key Packages
```
Django>=6.0
djangorestframework>=3.15
django-cors-headers>=4.4
psycopg>=3.2
django-allauth>=0.63
mozilla-django-oauth-toolkit>=2.5
PyJWT>=2.9
sympy>=1.13
numpy>=2.0
matplotlib>=3.9        # Server-side graphing fallback
Pillow>=11
python-dotenv>=1.0
gunicorn>=23.0
```

---

## 3. Frontend Structure

```
frontend/
├── src/
│   ├── api/                # Axios-based API clients
│   ├── assets/             # Static assets, SVGs
│   ├── components/         # Reusable UI components (shadcn/ui)
│   │   ├── ui/             # Base components (button, input, card...)
│   │   ├── calculator/     # Calculator-specific components
│   │   └── subjects/       # Subject-specific components
│   ├── features/           # Feature-based modules
│   │   ├── accounts/
│   │   ├── calculator/
│   │   ├── learning/
│   │   └── social/
│   ├── hooks/              # Custom React hooks
│   ├── i18n/               # translations
│   │   ├── en.json
│   │   ├── zh.json
│   │   └── fr.json
│   ├── lib/                # Utilities (validators, formatters)
│   ├── pages/              # Route-level components
│   ├── services/           # Business logic services
│   ├── types/              # TypeScript types
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

### Key Packages
```
react>=18.3
react-dom>=18.3
react-router-dom>=7
typescript>=5.7
vite>=6
tailwindcss>=4
@tailwindcss/vite>=4
yarn>=1.22
axios>=1.7
i18next>=24
react-i18next>=15
katex>=0.16       # Math formula rendering
mathjs>=13        # Expression parser + evaluator
plotly.js>=3      # Graphing (or use custom SVG)
p5>=1.11         # Creative coding / simulations
@phosphor-icons/react>=2
clsx>=2
tailwind-merge>=2
zod>=3
```

---

## 4. Database Schema (Phase 1)

### Users (Keycloak-managed)
```
keycloak_sub (UUID, PK) — from Keycloak
email (unique)
created_at
updated_at
```

### UserProfile (extended info)
```
user_id (FK → keycloak_sub)
display_name
avatar_url
language_preference (en|zh|fr)
timezone
bio
role (student|teacher|creator|admin)
is_active
```

### CustomFunctions (calculator)
```
id (UUID, PK)
user_id (FK)
name (varchar 64)
description (text)
parameters (JSON — [{name: "x", type: "number"}])
expression (text — the function body)
created_at
updated_at
is_public (boolean)
```

### Notes
```
id (UUID, PK)
user_id (FK)
title (varchar 255)
content (JSONB — block-based content)
subject (varchar 64) — math|physics|chemistry|biology|literacy|arts
tags (array)
created_at
updated_at
is_shared
```

### Questions
```
id (UUID, PK)
creator_id (FK)
type (mcq|numeric|proof|code|simulation)
subject (varchar 64)
difficulty (easy|medium|hard)
content (JSONB — block-based)
answer (JSONB)
hints (JSONB array)
tags (array)
is_public
approved
```

### QuestionSets
```
id (UUID, PK)
creator_id (FK)
title
description
questions (M2M → Questions)
subject
difficulty
time_limit (minutes)
created_at
```

---

## 5. API Design

### Authentication
- All API requests include `Authorization: Bearer <keycloak_access_token>`
- Django validates token against Keycloak's JWKS endpoint
- Token refresh handled client-side

### API Versioning
- `/api/v1/` prefix
- Format: `/api/v1/{resource}/{action}/`

### Key Endpoints

```
Auth:
  POST /api/v1/auth/token/verify/
  POST /api/v1/auth/token/refresh/

Profile:
  GET  /api/v1/accounts/profile/
  PUT  /api/v1/accounts/profile/

Calculator:
  GET  /api/v1/calculator/functions/         # List user's functions
  POST /api/v1/calculator/functions/        # Create function
  GET  /api/v1/calculator/evaluate/         # Evaluate expression
  GET  /api/v1/calculator/plot/             # Get plot data/SVG

Notes:
  GET/POST /api/v1/learning/notes/
  GET/PUT/DELETE /api/v1/learning/notes/{id}/

Questions:
  GET/POST /api/v1/learning/questions/
  GET/PUT /api/v1/learning/questions/{id}/

QuestionSets:
  GET/POST /api/v1/learning/question-sets/

Social:
  POST /api/v1/social/follow/{user_id}/
  DELETE /api/v1/social/follow/{user_id}/
  GET /api/v1/social/followers/
  GET /api/v1/social/following/
```

---

## 6. Calculator Engine Design

### Frontend (Primary)
- **Expression Input**: Custom input field with syntax highlighting
- **Parser**: `mathjs` for expression parsing and evaluation
- **Rendering**: `KaTeX` for formula display
- **Graphing**: Custom SVG renderer using Plotly.js or custom canvas

### Backend (Fallback)
- `/api/v1/calculator/evaluate/` — complex symbolic computation (SymPy)
- `/api/v1/calculator/plot/` — returns SVG for complex 3D plots
- Custom functions stored in DB, evaluated server-side with sandboxed Python

### Custom Function System
```
User defines: myFunc(x, y) = x^2 + sin(y)

Stored as:
{
  "name": "myFunc",
  "parameters": [{"name": "x", "type": "number"}, {"name": "y", "type": "number"}],
  "expression": "x^2 + sin(y)",
  "description": "Quadratic with sine"
}

Evaluation:
1. Validate parameters
2. Substitute into expression
3. Evaluate via mathjs (client) or SymPy (server)
```

---

## 7. i18n Strategy

### Backend
- Django's `gettext` for Python strings
- `django-modeltranslation` or manual fields for user-generated content

### Frontend
- `react-i18next` with JSON translation files
- Language switcher in user settings
- Default: browser language detection → fallback `en`

### Content
- Subject content stored with locale suffix (`content_en`, `content_zh`, `content_fr`)
- Or JSONB with locale keys

---

## 8. Phase 1 Deliverables

- [ ] Django project scaffolded with apps
- [ ] React frontend scaffolded with Vite + TailwindCSS
- [ ] Keycloak authentication working
- [ ] User profile CRUD
- [ ] Calculator: basic + advanced modes (trig, calculus, algebra)
- [ ] Custom function system (create, list, evaluate)
- [ ] SVG rendering for formulas and graphs
- [ ] i18n: EN/CN/FR
- [ ] docker-compose.yml for local dev

---

## 9. Dev Workflow

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Frontend
cd frontend
yarn install
yarn dev

# Both
docker compose up
```

---

## 10. Conventions

- **Branch naming**: `feature/<feature-name>`, `fix/<issue>`, `docs/<topic>`
- **Commit messages**: Conventional Commits (feat:, fix:, docs:, refactor:)
- **PRs**: Require at least 1 review before merge
- **Code style**: Black (Python), Prettier (JS/TS/JSON)
- **API responses**: Always JSON `{data, meta, error}`

---

_Last updated: 2026-05-10_