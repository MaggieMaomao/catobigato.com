# CatobiGato.com — Platform Requirements

## Overview
An all-ages online learning and practicing platform (leetincode-style) with subjects across math, physics, chemistry, biology, literacy, and arts. Built as a modular, scalable educational ecosystem.

---

## Audience
- **Primary**: K-12 students
- **Secondary**: All ages (expandable)
- **Content creators**: Platform admins, third-party educators
- **Location**: Canada (EN/CN/FR language support required from day one)

---

## Core Feature Groups

### 1. Calculator Engine
- Basic arithmetic calculator
- Advanced modes:
  - Trigonometric
  - Calculus (derivatives, integrals)
  - Algebra (equation solving, factorization)
  - Curve / Graph plotting
- Build-in function library (standard math functions)
- **Customizable user-defined functions** (Excel-like function system)
- Frontend SVG rendering (no server-side rendering for performance)
- Expression parser: client-side with fallback to backend for complex computation

### 2. Subject Modules
- **Math**: Calculator, graphing, symbolic math
- **Physics**: Animated formulas, concept visualization, simulation
- **Chemistry**: Molecular diagrams, reaction visualization
- **Biology**: Anatomy diagrams, process animations
- **Literacy**: Reading, writing, grammar tools
- **Arts**: Visual/creative tools
- All content rendered as SVG/animated SVG in frontend

### 3. User System
- Auth via Keycloak@KeyToMarvel.com (existing)
- User profiles with preferences
- Roles: Student, Teacher, Creator, Admin
- Permission model for third-party content creators

### 4. Learning Flow
- Notes (user-created)
- Question sets (curated + user-created)
- Exams (timed, scored)
- Correction study (review mistakes)
- Practice sessions
- AI checking + manual checking
- Statistics and reports

### 5. Puzzle & Question Bank
- Crawlers to ingest puzzles (future, copyright considerations)
- Manual puzzle creation (aligned with curriculum)
- Import/export puzzles
- Version control for puzzles

### 6. Social Features
- Follow/watch users
- Groups (study groups, classes)
- Communication (messaging, comments)
- Share study events via standard services (Google Calendar, etc.)

### 7. Platform Integrations
- Google Calendar (share study events)
- Gmail (notifications)
- Google Maps (location-based learning)
- WeChat (notifications for Chinese-speaking users)

---

## Technical Decisions

### Architecture
- **Pattern**: Modular Monolith (Django)
- **Future**: Microservices when scaling requires
- **Reason**: Features interact heavily; avoid distributed systems complexity early

### Tech Stack
- **Backend**: Python, Django 5+, Django REST Framework
- **Frontend**: React 18+, TypeScript, TailwindCSS, Vite, Yarn
- **Database**: PostgreSQL 16+
- **Auth**: Keycloak (KeyToMarvel.com) via OIDC
- **Content**: Block-based model (polymorphic — text, math, formula, animation, image)
- **Rendering**: Frontend SVG (KaTeX, Manim-style animations, p5.js)

### Database Design Principles
- Block-based content model (Notion-like)
- Polymorphic content for heterogeneous data (questions, notes, formulas)
- Shared user table (Keycloak sub as primary key)
- Per-feature Django apps with clear boundaries

### i18n
- English (en), Chinese (zh), French (fr)
- Django's i18n framework + frontend react-i18next
- All user-facing strings externalized

---

## Phased Roadmap

### Phase 1 — MVP
- Project scaffolding (Django + React)
- Keycloak authentication integration
- User profiles
- Calculator engine (basic + advanced modes)
- Custom function system (user-defined functions)
- SVG-based formula rendering (KaTeX)
- i18n (EN/CN/FR)

### Phase 2 — Core Learning
- Notes system
- Question sets
- Exams with basic grading
- User-created content (with permission model)

### Phase 3 — Advanced Learning
- AI checking (symbolic math grading, LLM for essays)
- Physics/Chemistry/Biology content modules
- Animated concept visualizations
- Statistics and reports

### Phase 4 — Content Ecosystem
- Puzzle management system
- Crawler infrastructure (future)
- Curriculum-aligned content creation tools
- Content approval workflow

### Phase 5 — Social
- Follow/watch system
- Groups
- Basic messaging

### Phase 6 — Integrations
- Google Calendar, Gmail, Maps, WeChat

---

## Open Questions
- [ ] Copyright policy for crawled puzzles
- [ ] AI checking specifics per subject (symbolic vs LLM)
- [ ] Content creation permission tiers (which roles can publish)
- [ ] Analytics and learning analytics data model
- [ ] Payment model (free tier? subscription?)

---

_Last updated: 2026-05-10_