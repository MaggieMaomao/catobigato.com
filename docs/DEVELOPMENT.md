# CatobiGato Development Tracker

## Current Status

**Phase 1 — MVP Core ✅ COMPLETE**

## Phase Status

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| Phase 1 | MVP Core | ✅ Done | Backend running at :8001, auth integrated, DB migrated |
| Phase 2 | Learning Module | 🔲 Pending | Notes block editor, Question Sets, Exams |
| Phase 3 | Calculator Engine | 🔲 Pending | Advanced modes, graphing, custom function system |
| Phase 4 | Puzzles Module | 🔲 Pending | Crawlers, manual creation, import |
| Phase 5 | Social Features | 🔲 Pending | Follow, groups, messaging |
| Phase 6 | Platform Integrations | 🔲 Pending | Google Calendar, Gmail, WeChat |
| Phase 7 | Subject Modules | 🔲 Pending | Physics, Chemistry, Biology, Arts |

---

## Environment Info

### Backend
- **Running on**: `http://localhost:8001` (port 8000 occupied by FlowDesk API)
- **Python**: 3.12.3 in `backend/venv/`
- **Database**: PostgreSQL `catobigato` at `localhost:5432`
  - Role: `catobigato` / `CatoBigato2026!`
  - Owner: `catobigato`
- **Django settings**: environment-aware dispatch via `catobigato/settings/__init__.py`
  - `DJANGO_ENV=development` → `development.py`
  - `DJANGO_ENV=production` → `production.py`
- **Start command**: `source venv/bin/activate && python manage.py runserver 0.0.0.0:8001`

### Frontend
- **Dev server**: `http://localhost:5173`
- **Stack**: React 18 + TypeScript + Vite + Tailwind CSS 4 + Yarn
- **Build**: `yarn build` ✅ passes (built in ~3.7s)
- **Key packages**: `keycloak-js@26.2.4`, `axios`, `react-router-dom`, `i18next`, `react-i18next`, `katex`, `sympy`

### Keycloak (KeyToMarvel.com)
- **Realm**: `catobigato` (pre-created)
- **Client ID**: `catobigato`
- **Client Secret**: `qXhU9L8p8BDdXBAHpBPpx0e22qsX5GUJ`
- **URL**: `https://www.keytomarvel.com`
- **OIDC Discovery**: `https://www.keytomarvel.com/realms/catobigato/.well-known/openid-configuration`

---

## Backend Structure

```
backend/
├── apps/
│   ├── accounts/          # Keycloak JWT auth + UserProfile + Follow
│   │   ├── models.py      # UserProfile (keycloak_sub), UserFollow
│   │   ├── views.py       # Profile CRUD, follow/unfollow, followers/following lists
│   │   ├── serializers.py # UserProfileSerializer, FollowersSerializer, etc.
│   │   ├── urls.py        # /api/v1/accounts/*
│   │   └── authentication.py  # KeycloakAuthentication (JWT RS256 via JWKS)
│   ├── calculator/        # SymPy math engine + CustomFunction registry
│   │   ├── engine.py      # CalculatorEngine (SymPy-based, 8 modes)
│   │   ├── models.py      # CustomFunction, CalculationHistory
│   │   ├── views.py       # evaluate, simplify, factor, expand, solve, derivative, integrate, plot, functions CRUD
│   │   ├── serializers.py # CustomFunctionSerializer, HistorySerializer
│   │   └── urls.py        # /api/v1/calculator/*
│   ├── learning/          # Notes, QuestionSets, Exams (models+stubs ready)
│   │   ├── models.py      # Note (JSON blocks), QuestionSet, Exam, ExamAttempt
│   │   ├── views.py       # Stub endpoints (planned for Phase 2)
│   │   └── urls.py        # /api/v1/learning/*
│   ├── puzzles/           # Puzzle, PuzzleSource (models+stubs ready)
│   │   ├── models.py      # Puzzle, PuzzleSource, Tag
│   │   ├── views.py       # Stub endpoints (planned for Phase 4)
│   │   └── urls.py        # /api/v1/puzzles/*
│   ├── social/            # Messaging, Groups (models+stubs ready)
│   │   ├── models.py      # Conversation, Message, Group, GroupMembership
│   │   ├── views.py       # Stub endpoints (planned for Phase 5)
│   │   └── urls.py        # /api/v1/social/*
│   └── core/              # Shared utilities, middleware, decorators
├── catobigato/
│   ├── settings/
│   │   ├── __init__.py    # Auto-detects DJANGO_ENV → loads correct env settings
│   │   ├── base.py        # Base config (INSTALLED_APPS, MIDDLEWARE, rest_framework, cors, i18n, etc.)
│   │   ├── development.py # Dev overrides (DEBUG=True, CORS_ALLOW_ALL_ORIGINS=True)
│   │   ├── production.py  # Prod overrides (env vars, SSL, strict CORS)
│   │   └── testing.py     # Test overrides (SQLite, no CORS)
│   ├── urls.py            # Main URL routing (admin, health, api/v1/)
│   └── wsgi.py
├── venv/                  # Python virtual environment
├── requirements.txt
├── manage.py
├── .env                   # Local env vars (gitignored)
└── .env.example           # Template for .env
```

---

## Frontend Structure

```
frontend/
├── src/
│   ├── App.tsx            # BrowserRouter + sticky nav + auth + lazy pages
│   ├── auth/
│   │   └── keycloak.ts    # Keycloak-js singleton, configured for catobigato realm
│   ├── hooks/
│   │   └── useAuth.ts     # useAuth hook — login/logout/register/isAuthenticated/user info
│   ├── api/
│   │   └── index.ts       # Axios client + interceptors + typed API functions
│   ├── i18n/
│   │   ├── index.ts       # i18next configuration
│   │   └── locales/
│   │       ├── en.json
│   │       ├── zh.json
│   │       └── fr.json
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── CalculatorPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── LearningPage.tsx   # stub — Phase 2
│   │   ├── PuzzlesPage.tsx    # stub — Phase 4
│   │   ├── SocialPage.tsx     # stub — Phase 5
│   │   ├── KeycloakCallback.tsx
│   │   └── LoginError.tsx
│   └── index.css          # Tailwind 4 @import, CSS variables, KaTeX fonts, custom scrollbar
├── public/
│   ├── silent-check-sso.html  # Keycloak PKCE silent SSO
│   └── favicon.ico
├── index.html
├── package.json
├── vite.config.ts         # @tailwindcss/vite plugin, path aliases
├── tsconfig.json
├── .env                   # VITE_KEYCLOAK_*, VITE_API_BASE_URL (gitignored)
└── .env.example
```

---

## API Endpoints

### Public (No Auth)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/` | Health check |
| POST | `/api/v1/calculator/evaluate/` | Evaluate math expression |
| POST | `/api/v1/calculator/simplify/` | Simplify expression |
| POST | `/api/v1/calculator/solve/` | Solve equation |
| POST | `/api/v1/calculator/derivative/` | Compute derivative |
| POST | `/api/v1/calculator/integrate/` | Compute integral |
| POST | `/api/v1/calculator/plot/` | Generate SVG plot |
| GET | `/api/v1/learning/notes/` | Notes stub (Phase 2) |
| GET | `/api/v1/learning/questions/` | Questions stub |
| GET | `/api/v1/learning/question-sets/` | Question sets stub |
| GET | `/api/v1/puzzles/puzzles/` | Puzzles stub |
| GET | `/api/v1/puzzles/sources/` | Puzzle sources stub |
| GET | `/api/v1/social/conversations/` | Conversations stub |
| GET | `/api/v1/social/messages/` | Messages stub |

### Auth-Required (Keycloak JWT Bearer)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/accounts/profile/` | Get/update own profile |
| GET | `/api/v1/accounts/profile/<uuid>/` | Get any user's public profile |
| POST | `/api/v1/accounts/follow/<uuid>/` | Follow a user |
| DELETE | `/api/v1/accounts/follow/<uuid>/` | Unfollow a user |
| GET | `/api/v1/accounts/followers/` | List my followers |
| GET | `/api/v1/accounts/following/` | List who I follow |
| GET | `/api/v1/accounts/follow-status/<uuid>/` | Check mutual follow status |
| GET | `/api/v1/calculator/functions/` | List custom functions |
| POST | `/api/v1/calculator/functions/` | Create custom function |
| PUT | `/api/v1/calculator/functions/<id>/` | Update custom function |
| DELETE | `/api/v1/calculator/functions/<id>/` | Delete custom function |
| GET | `/api/v1/calculator/history/` | Get calculation history |
| DELETE | `/api/v1/calculator/history/` | Clear history |

---

## Database Tables

All created via `python manage.py migrate`:
- `accounts_userprofile` — user profile linked to Keycloak sub
- `accounts_userfollow` — follower/following relationships
- `calculator_customfunction` — user-defined functions with params/body
- `calculator_calculationhistory` — history entries with SVG plot data
- `learning_note` — notes with JSON block content
- `learning_questionset` — grouped questions
- `learning_exam` — exam definitions
- `learning_examattempt` — exam attempts by users
- `puzzles_puzzlesource` — puzzle source (manual/crawled)
- `puzzles_puzzle` — puzzles with JSON content
- `puzzles_tag` — puzzle tags
- `social_conversation` — direct or group conversations
- `social_message` — messages
- `social_group` — social groups
- `social_groupmembership` — group memberships

---

## Running Commands

```bash
# Backend
cd /home/whereq/github/catobigato.com/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8001     # start dev server
python manage.py check                          # verify config (should show no issues)
python manage.py makemigrations                  # create migrations after model changes
python manage.py migrate                         # apply migrations

# Frontend
cd /home/whereq/github/catobigato.com/frontend
yarn dev                                        # start dev server (http://localhost:5173)
yarn build                                      # production build → dist/
```

---

## Key Design Decisions

### Auth: Keycloak-only, no local password auth
- No `AbstractUser` or custom User model with passwords
- `keycloak_sub` is the single source of user identity
- `UserProfile` auto-created on first API access
- JWT RS256 validation via Keycloak's JWKS endpoint (no shared secret)
- Frontend uses `keycloak-js` with PKCE for login flow

### Settings dispatch: `DJANGO_ENV`-aware
- `catobigato/settings/__init__.py` auto-imports based on `DJANGO_ENV`
- Default: `development` if `DJANGO_ENV` not set
- No hardcoding of env-specific values in `base.py`

### Custom function system: SymPy expression-based (not eval)
- User-defined functions stored in `calculator_customfunction` table
- Parameters and body stored as strings, executed via SymPy `sympify`
- No `eval()` — safe symbolic math execution only
- Supports: `def myfunc(x, y) = x^2 + y` syntax

### Block-based content model for Notes
- Notes stored as JSON array of blocks in `Note.content JSONField`
- Block types: `text`, `math` (LaTeX), `formula` (KaTeX render), `code`, `image`, `divider`
- Frontend renders each block with appropriate component
- Reorderable, editable, deletable blocks

### Database: dedicated role, not superuser
- `catobigato` role owns `catobigato` database
- `whereq` superuser used only for initial DB/role creation
- Connection from Django uses `catobigato` role with `CatoBigato2026!`

---

## Development Notes

- Port 8000 occupied by `flowdesk-api` (LXD container) — CatobiGato uses 8001
- `DJANGO_SETTINGS_MODULE=catobigato.settings` works because `__init__.py` dispatches to correct env
- Keycloak JWT `aud` claim must match `KEYCLOAK_CLIENT_ID` (`catobigato`)
- Tailwind CSS v4 uses `@tailwindcss/vite` plugin (not PostCSS), `@import "tailwindcss"` directive
- React lazy loading used for non-critical pages (Learning, Puzzles, Social) — no `<Suspense>` wrapper needed with Vite
- `kaTeX` fonts bundled in `index.css` to avoid CDN dependency for math rendering

---

## Phase 2 Plan: Learning Module

**Goal**: Block-based Notes editor with CRUD

### Backend
- [ ] `Note` model — already exists with JSON `content` field
- [ ] CRUD views for `/api/v1/learning/notes/`
- [ ] Share notes (public/private) via `Note.is_public` + view permission
- [ ] Tags for notes

### Frontend
- [ ] `NotesPage.tsx` — list view of user's notes
- [ ] `NoteEditor.tsx` — block-based editor
  - Block types: `text`, `math` (LaTeX input → KaTeX preview), `code`, `image`
  - Add/delete/reorder blocks
  - Auto-save on change (debounced)
- [ ] `/learning/notes` route → authenticated only