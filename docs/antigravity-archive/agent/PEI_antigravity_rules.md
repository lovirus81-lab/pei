# PEI Project Rules

## Project Identity
- Project: PEI (Plant Engineering IDE)
- Purpose: 규격 기반 PFD/P&ID 검증 및 생성 웹 플랫폼
- Core Value: "규격에 부합하는 설계를 제공한다"

## Tech Stack (Do NOT deviate)
- Frontend: React 18 + TypeScript 5 + Vite
- Canvas: ReactFlow (node-edge graph)
- State: Zustand
- Backend: FastAPI (Python 3.12, async)
- ORM: SQLAlchemy 2.0 (async)
- DB: SQLite (MVP) → PostgreSQL (SaaS)
- Migration: Alembic
- Lint: ruff (Python), ESLint + Prettier (TS)

## Architecture Rules

### Canonical ↔ UI Separation
- NEVER store ReactFlow JSON directly in DB
- ALWAYS convert through `converters/` (to-canonical.ts, to-reactflow.ts)
- Canonical schema is the single source of truth for diagrams
- Both schemas MUST have a `schema_version` field

### Ruleset Versioning
- Every ruleset MUST have: id, name, version, hash, status
- `hash` is SHA-256 of all rules content — compute on every save
- Every validation run MUST record: diagram_version + ruleset_id + ruleset_hash
- This enables audit: "diagram v3 passed ruleset v1 (hash=abc)"

### services/ Boundary Rules (CRITICAL)
- NEVER import FastAPI objects (Request, Depends, HTTPException) in services/
- NEVER create DB sessions inside services — inject as function argument
- ALL service function I/O MUST use Pydantic schemas from schemas/
- This enables future extraction to domain/ layer

### Frontend reference/ (NOT rules/)
- Frontend `reference/` folder contains CACHE ONLY — not business logic
- Source of truth for all rules is ALWAYS backend DB
- reference/ data is fetched from GET /reference/* on app init

### Generator Pattern
- generator.py is ONE file with THREE entry points:
  - `generate_template(canonical, ruleset) -> canonical`
  - `auto_repair(canonical, validation_report, ruleset) -> canonical`
  - `ai_assist(prompt, canonical, ruleset) -> patch`
- Do NOT split into 3 modules until file exceeds 500 lines

### Export Bundle
- Export is ALWAYS a ZIP bundle, never a single file
- Bundle MUST contain: manifest.json (sha256), run_meta.json, diagram.json, ruleset_ref.json
- validation_report.json and deliverables/ are optional

## Code Style

### Python
- Use type hints everywhere
- Pydantic v2 models for all schemas
- Async functions for all DB operations
- f-strings for string formatting
- Korean comments for domain logic, English for technical comments

### TypeScript
- Strict mode always on
- Interface over Type for object shapes
- Functional components only (no class components)
- Custom hooks for shared logic

## File Naming
- Python: snake_case (validator.py, canonical.py)
- TypeScript: kebab-case (to-canonical.ts, equipment-node.tsx)
- Components: PascalCase (EquipmentNode.tsx, PropertyPanel.tsx)
- SVG symbols: kebab-case (check-valve.svg, centrifugal-pump.svg)

## Commit Messages
- Format: `type(scope): message`
- Types: feat, fix, refactor, docs, test, chore
- Scope: frontend, backend, db, docs, ops
- Examples:
  - `feat(backend): add validation engine with graph pattern matching`
  - `fix(frontend): fix canonical conversion for instrument nodes`
  - `docs(db): update seed data with 10 new piping rules`

## Testing
- Backend: pytest with async fixtures
- Frontend: vitest for unit, playwright for e2e (later)
- Minimum: test all services/ functions
- Seed data validation: test that all 110 rules load without error

## What NOT to Do
- Do NOT use Neo4j or any graph DB — use JSON + in-memory graph
- Do NOT add authentication in MVP
- Do NOT create separate CSS files — use Tailwind utilities
- Do NOT add WebSocket for real-time — use polling/debounce for MVP
- Do NOT copy ISA standard text verbatim into code or DB

## Git Policy
- ALWAYS commit after completing each task with Conventional Commits format
- NEVER push without user approval
- NEVER use --force flag