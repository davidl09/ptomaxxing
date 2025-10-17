# AGENTS.md — Max Days Off Project

This document defines coding guidelines, conventions, and checklists for contributors and AI agents implementing and maintaining the **Max Days Off** feature using **FastAPI (Python)** and **Bun + Vite + React + TypeScript**. Follow these rules to ensure code quality, consistency, and safe deployments.

---

## 0) Non‑Negotiables
- **Correctness first**, then performance. Prefer readable, testable code.
- **Type safety everywhere** (Python + TS). Treat warnings as build failures.
- **Deterministic outputs** for identical inputs (same year/locale/params → same plan ordering).
- **No hidden state** across requests. All state must be explicit (request body/URL params).
- **No PII persistence**. Parameters may be logged at INFO only if scrubbed.
- **Timezones**: Use `zoneinfo` everywhere; never hardcode offsets.

---

## 1) Repository Hygiene
- Monorepo layout:
```
backend/
  app/
    api/            # FastAPI routes
    core/           # config, locale helpers
    domain/         # calendar, candidates, selection, scoring, models
    services/       # ics export, caching
    tests/          # unit + integration
frontend/
  src/
    api/            # API client + types
    components/     # Presentational + composite components
    hooks/          # React hooks
    pages/          # Planner page
    utils/          # date & formatting utils
```
- Keep modules ≤400 LOC. If bigger, split by concern.
- Every new module must ship with tests and docstrings. No dead code.

---

## 2) Python (FastAPI) Standards
- **Version**: Python 3.11+.
- **Formatting/Linting**: `black`, `ruff`, `isort`. CI must fail on lint.
- **Typing**: `mypy --strict`. Avoid `Any`. Use typed `dict`/`TypedDict`/`Protocol` when needed.
- **Models**: Pydantic v2 models for DTOs. Validate at boundary; keep domain types plain dataclasses where suitable.
- **Dates**:
  - Always use `date` (no time) for all‑day logic; convert to `datetime` only for ICS stamps.
  - Use `zoneinfo.ZoneInfo(tz)` for timezone operations.
- **Holidays**: `holidays` (python‑holidays) with `observed=True`. Normalize country/subdivision codes in one place `core/locale.py`.
- **Configuration**: Centralize in `core/config.py` (pydantic `BaseSettings`). No inline env lookups.
- **Errors**: Raise `HTTPException` with machine‑readable payload `{ code, message, hint }`. Don’t leak stack traces.
- **Logging**: `structlog` or stdlib logging with JSON formatter at INFO. Include `request_id`, `year`, `country`, `region` in context.
- **Cache**: Read‑through in‑memory cache (or Redis if available) for holidays by `(year,country,region)`.
- **ICS**: Use `icalendar` or `ics` lib. All‑day events for blocks; separate all‑day events for PTO vs Holiday are optional but must include categories.
- **Determinism**: Sort candidates by `(end_date, start_date)`; tie‑break by PTO density, then lexicographic date.

### Python Code Style Examples
- Prefer composition over inheritance in domain modules.
- Functions must be ≤50 LOC where possible; refactor helpers.
- Public functions require docstrings (Google style) and examples.

---

## 3) Frontend (Bun + Vite + React + TypeScript)
- **TypeScript**: `"strict": true`. No `any`/`unknown` at boundaries. Use `zod` or `valibot` to runtime‑validate API responses.
- **State**: Use React Query (TanStack) for server data; local UI state in components or small hooks. No global singletons.
- **Data Fetch**: Centralize `api/client.ts` with typed wrappers. Query keys must include **all** params influencing responses.
- **Components**: Functional components with hooks only. Keep presentational vs. container split clear.
- **Dates/UI**: Use `date-fns` and `Intl.DateTimeFormat` for formatting; never use Moment.
- **Accessibility**: WCAG 2.1 AA. All interactive elements keyboard‑navigable. Provide ARIA labels for calendar cells and legends.
- **Styling**: Tailwind or minimal CSS modules. No global CSS leaks. Use semantic HTML for lists and headings.
- **Routing/Share Links**: Persist planner params in the URL query; decode safely and validate.
- **Error UX**: Friendly, actionable messages. Show server `hint` if provided.

### TS/React Do/Don’t
- ✅ Narrow types at boundaries (`as const` where appropriate).  
- ✅ Memoize expensive computations (`useMemo`) and event handlers (`useCallback`).  
- ❌ Don’t pass dates as strings without parsing and validating.  
- ❌ Don’t mutate arrays/objects; use immutable updates.

---

## 4) API Contracts & Versioning
- All routes prefixed with `/api/max-days-off`.
- Every endpoint must have OpenAPI schemas with examples.
- Version via proxy routing or header if a breaking change is unavoidable. Prefer additive changes.
- Keep server and client DTOs in sync:
  - Backend: export `openapi.json` in CI.
  - Frontend: generate types (`openapi-typescript`) or maintain hand‑written `types.ts` with tests.

---

## 5) Planning & Algorithm Rules
- Input normalization occurs once at the API boundary.
- Day labeling pipeline: weekend → holiday overlay → workday fallback.
- Candidate windows:
  - Seed around each holiday (±7 days default), include weekend extensions, and double‑holiday spans (≤14 days gap).
  - Discard windows that violate blackout ranges or min/max block length.
- Scoring:
  - `value = off_streak − λ*pto_needed + seasonal_bonus` (λ default 0.25).
  - Seasonal bonus applies when blocks fall in distinct quarters.
- Selection:
  - Enforce **non‑overlap**, PTO budget, and `blocks_max`.
  - For `max_longest`, choose best single window first, then fill greedily with non‑overlapping best density windows.
- Output must include: total PTO used, consecutive days per block, PTO day list, weekends, holidays, and human explanation.

---

## 6) Testing Policy
- **Unit (backend)**:
  - Holiday labeling for at least 4 locales (US‑CA, CA‑ON, GB‑ENG, AU‑NSW).
  - Candidate generation around Tue/Thu holidays; weekend extension; double‑holiday windows.
  - Selection correctness: budget, non‑overlap, `blocks_max`.
- **Unit (frontend)**:
  - Render BlocksList and MiniMonthStrip with mocked data; a11y snapshot checks.
  - URL → state hydration and back/forward navigation.
- **Integration**:
  - E2E: POST `/plan` with realistic params returns 3–5 plans < 1s.
  - ICS export imports into Google Calendar (validate `VTIMEZONE`, all‑day spans).
- **Contract**:
  - Assert API examples in CI (Dredd/Prism or schema validation tests).
- **Performance**:
  - Budget: planning under 150ms p50 with PTO ≤ 25 and ≤ 5 blocks. Add benchmarks.

---

## 7) Security & Privacy
- No user identifiers required; if authenticated, don’t store parameters beyond transient cache.
- Input validation and allow‑lists for country/region codes.
- Rate limiting (30 rpm/IP) and CORS allow‑list.
- Structured logs; avoid logging full request bodies. Redact arrays of dates if necessary.
- Keep dependencies minimal and pinned; weekly dependency audit.

---

## 8) Git Workflow & Reviews
- Branch naming: `feature/<short-name>`, `fix/<short-name>`, `chore/<short-name>`.
- Commits: Conventional Commits (`feat: ...`, `fix: ...`, `refactor: ...`).
- PR Template must include:
  - Scope & screenshots (for UI).
  - Checklist: tests, types, docs, perf, a11y.
  - Risk and rollback plan.
- Reviews: at least 1 reviewer; agents must self‑review with lint/test passing before opening PR.

---

## 9) CI/CD Requirements
- **Backend**: run `ruff`, `black --check`, `isort --check`, `mypy`, unit + integration tests, export OpenAPI.
- **Frontend**: `eslint --max-warnings=0`, `tsc --noEmit`, unit tests, Lighthouse CI for planner page.
- Build artifacts versioned with git SHA. Feature flags **not used** for this project; ship complete slices.

---

## 10) Developer Experience
- Provide `make`/`bun` scripts:
```
make dev           # run backend (uvicorn) and frontend (vite) concurrently
make test          # run all tests
make fmt           # format + lint backend
make typecheck     # mypy + tsc
```
- Seed fixtures for a small set of locales/years to develop deterministically.

---

## 11) UX Specifics to Honor
- Calendar strips must visually distinguish Weekend / Holiday / PTO with a legend.
- Plan Summary Bar: “Plan A: 22 days off using 8 PTO across 3 blocks”.
- Export buttons: ICS full plan or per block. Copy PTO days → clipboard as newline dates `YYYY‑MM‑DD`.
- Shareable URL encodes all planner params.
- Error empty state: Offer concrete next steps (e.g., “reduce min block length”, “increase PTO”).

---

## 12) Code Examples & Snippets (Conventions)
### Backend error response shape
```json
{
  "error": { "code": "INVALID_INPUT", "message": "blocks_max must be between 1 and 5", "hint": "Try 1–5" }
}
```

### Typed React Query key pattern
```ts
const key = [
  'plan',
  { year, country, region, ptoTotal, blocksMax, goal, weekend, prefs, constraints }
] as const;
```

### Date formatting
```ts
new Intl.DateTimeFormat(locale || 'en-CA', { weekday: 'short', month: 'short', day: 'numeric' }).format(date)
```

---

## 13) Definition of Done (per PR)
- ✅ Lint/type/test all green in CI.
- ✅ Contract examples updated and verified.
- ✅ Benchmarks within budget; no regressions.
- ✅ A11y checks pass on new UI.
- ✅ Docs updated (this file or inline module docs).

---

## 14) Anti‑Patterns (Do Not Do)
- ❌ Hardcoding holiday lists in the frontend.
- ❌ Relying on local time when computing windows; always use target timezone.
- ❌ Using `any`/`dict` with mixed shapes; define explicit types.
- ❌ Performing selection with unstable sorts; tie‑break deterministically.
- ❌ Logging raw request bodies with full date arrays.

---

## 15) Maintainers & Ownership
- **Domain logic**: `backend/app/domain/*` — tests required for every change.
- **API shape**: `backend/app/api/*` — owner must update OpenAPI + client types.
- **UI**: `frontend/src/components/*` — owner ensures a11y and responsive behavior.
- **Build/CI**: `/.github/workflows/*` — owner ensures deterministic builds and pinning.

---

## 16) Quickstart Scripts
- Backend:
```
uv sync && uv run fastapi dev  # or poetry/pip as per repo tool
```
- Frontend:
```
bun install && bun dev
```

---

Adhere to this guide to keep contributions safe, consistent, and production‑ready. If a rule conflicts with correctness, escalate in the PR and propose a targeted exception with tests.

