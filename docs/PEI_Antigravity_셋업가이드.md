# PEI — Antigravity 개발 환경 준비 가이드

---

## 1. 파일 배치 구조

Antigravity에서 PEI 프로젝트를 열면 아래 구조가 필요합니다.

```
pei/
├── .agent/                          # Antigravity 워크스페이스 설정
│   ├── rules.md                     # 프로젝트 규칙 (에이전트 행동 제약)
│   └── skills/                      # 프로젝트 전용 스킬
│       ├── rule-db/
│       │   └── SKILL.md             # 규칙 DB 관리 스킬
│       ├── canonical-schema/
│       │   └── SKILL.md             # Canonical 스키마 스킬
│       └── svg-symbols/
│           └── SKILL.md             # SVG 심볼 디자인 스킬
│
├── .context/                        # Knowledge Base (지식 베이스)
│   └── knowledge.md                 # 프로젝트 컨텍스트 문서
│
├── frontend/                        # (개발 시 생성)
├── backend/                         # (개발 시 생성)
├── db/seeds/                        # (개발 시 생성)
├── docs/                            # 설계 문서
│   ├── PEI_프로젝트구조_v2.md
│   ├── PEI_규격DB_스키마_규칙100건.md
│   ├── PEI_백엔드API_설계서.md
│   ├── PEI_프론트엔드캔버스_설계서.md
│   └── PEI_예시_PLA_PID_시나리오.md
├── ops/
├── .editorconfig
├── .pre-commit-config.yaml
├── ruff.toml
├── Makefile
└── README.md
```

---

## 2. 준비 파일 목록

### 2.1 Antigravity 전용 파일 (4개)

| 파일 | 용도 | 에이전트가 보는 시점 |
|---|---|---|
| `.agent/rules.md` | 프로젝트 규칙 — 기술 스택, 아키텍처 제약, 코드 스타일 | 항상 (모든 작업) |
| `.context/knowledge.md` | 프로젝트 컨텍스트 — 도메인 용어, 구조, 워크플로우 | 항상 (지식 베이스) |
| `.agent/skills/rule-db/SKILL.md` | 규칙 DB 작업 스킬 — 규칙 코드 체계, JSON 구조, 테스트 패턴 | 규칙 관련 작업 시 |
| `.agent/skills/canonical-schema/SKILL.md` | Canonical 스키마 스킬 — 노드/엣지 타입, 태그 규칙, 변환 규칙 | 스키마 관련 작업 시 |
| `.agent/skills/svg-symbols/SKILL.md` | SVG 심볼 스킬 — 심볼 디자인 규칙, 포트 위치, 크기 기준 | 심볼 작업 시 |

### 2.2 프로젝트 초기 설정 파일 (5개)

| 파일 | 내용 |
|---|---|
| `.editorconfig` | 들여쓰기, 줄 끝, 인코딩 통일 |
| `ruff.toml` | Python 린트/포맷 설정 |
| `.pre-commit-config.yaml` | 커밋 전 자동 검사 |
| `Makefile` | 표준 명령어 (dev, test, lint, db-seed) |
| `README.md` | 프로젝트 소개 + 빠른 시작 |

### 2.3 설계 문서 (5개) — docs/ 폴더

이미 작성 완료. Antigravity 에이전트가 참조할 수 있도록 docs/에 배치.

---

## 3. 셋업 절차

### Step 1: 프로젝트 폴더 생성

```bash
mkdir pei && cd pei
git init
```

### Step 2: Antigravity 파일 배치

```bash
# 규칙 + 스킬 + 지식베이스
mkdir -p .agent/skills/rule-db
mkdir -p .agent/skills/canonical-schema
mkdir -p .agent/skills/svg-symbols
mkdir -p .context
mkdir -p docs
```

첨부된 파일들을 해당 위치에 복사:
- `rules.md` → `.agent/rules.md`
- `knowledge.md` → `.context/knowledge.md`
- 스킬 SKILL.md 3개 → `.agent/skills/*/SKILL.md`
- 설계문서 5개 → `docs/`

### Step 3: 초기 설정 파일 생성

```bash
# .editorconfig, ruff.toml, .pre-commit-config.yaml, Makefile, README.md
# (아래 섹션 4의 내용을 각 파일로 생성)
```

### Step 4: Antigravity에서 열기

```bash
agy .    # 또는 Antigravity에서 Open Folder → pei/
```

### Step 5: 에이전트 설정

- Mode: **Review-driven development** (추천 — 에이전트가 계획을 보여주고 승인 후 실행)
- Terminal Policy: **Auto** (일반 명령은 자동, 위험 명령은 확인)
- Model: **Claude Sonnet 4.5** 또는 **Gemini 3 Pro**

### Step 6: 첫 번째 태스크

Agent Manager에서 New Task:

```
PEI 프로젝트 초기 셋업을 진행해주세요.

1. frontend/ 생성: Vite + React 18 + TypeScript, ReactFlow + Zustand 설치
2. backend/ 생성: FastAPI + SQLAlchemy 2.0 + Alembic, pyproject.toml 사용
3. DB 스키마 생성: docs/PEI_규격DB_스키마_규칙100건.md 참조하여 SQLAlchemy 모델 생성
4. 시드 데이터 생성: 110건 규칙을 db/seeds/ JSON 파일로 변환
5. seed_loader.py 구현: JSON → DB 로딩
6. 기본 API 구현: GET /reference/isa-codes, GET /reference/equipment-classes
7. 프론트에서 빈 ReactFlow 캔버스 렌더링 확인

.agent/rules.md와 docs/ 문서를 반드시 참조하세요.
```

---

## 4. 초기 설정 파일 내용

### .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[Makefile]
indent_style = tab
```

### ruff.toml

```toml
target-version = "py312"
line-length = 100

[lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
ignore = ["E501"]

[format]
quote-style = "double"
indent-style = "space"
```

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

### Makefile

```makefile
.PHONY: dev dev-front dev-back fmt lint test db-migrate db-seed db-reset up down

# 개발
dev:
	@echo "Starting frontend and backend..."
	$(MAKE) -j2 dev-front dev-back

dev-front:
	cd frontend && npm run dev

dev-back:
	cd backend && uvicorn app.main:app --reload --port 8000

# 코드 품질
fmt:
	cd backend && ruff format .
	cd frontend && npx prettier --write src/

lint:
	cd backend && ruff check .
	cd frontend && npx eslint src/

test:
	cd backend && pytest -v
	cd frontend && npx vitest run

# DB
db-migrate:
	cd backend && alembic upgrade head

db-seed:
	cd backend && python -m app.services.seed_loader

db-reset:
	rm -f backend/data/pei.db
	$(MAKE) db-migrate
	$(MAKE) db-seed

# Docker
up:
	cd ops && docker compose up -d

down:
	cd ops && docker compose down
```

### README.md

```markdown
# PEI — Plant Engineering IDE

규격 기반 PFD/P&ID 검증 및 생성 웹 플랫폼

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Git

### Setup
git clone <repo> && cd pei
cd frontend && npm install
cd ../backend && pip install -e ".[dev]"
make db-reset
make dev

### Architecture
- Frontend: React + TypeScript + ReactFlow (port 5173)
- Backend: FastAPI + SQLAlchemy (port 8000)
- DB: SQLite (backend/data/pei.db)

### Docs
See `docs/` for design specifications.
```

---

## 5. Antigravity 에이전트 활용 팁

### 태스크 분리 원칙

Antigravity는 멀티 에이전트로 병렬 작업이 가능합니다. PEI에서는 이렇게 분리하는 게 효과적입니다:

| 에이전트 | 태스크 | 독립성 |
|---|---|---|
| Agent A | 백엔드 API + DB 스키마 | 프론트와 독립 |
| Agent B | 프론트 캔버스 + 컴포넌트 | 백엔드와 독립 (Mock API) |
| Agent C | 시드 데이터 + 규칙 JSON | 코드와 독립 |
| Agent D | SVG 심볼 제작 | 완전 독립 |

### Plan 모드 사용

복잡한 기능(검증 엔진, Canonical 변환)은 **Plan 모드**에서 계획을 먼저 확인한 후 실행하세요. Fast 모드는 단순한 파일 생성, 수정에만 사용.

### Knowledge Base 활용

에이전트가 PEI 도메인을 모를 수 있으므로, `.context/knowledge.md`에 도메인 용어와 규칙을 상세히 작성해두었습니다. 에이전트가 ISA 코드나 장비 태그를 잘못 쓰면 Knowledge Base를 업데이트하세요.
