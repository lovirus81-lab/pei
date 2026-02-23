# PEI 프로젝트 구조 정의서 v2 (리뷰 반영)

---

## 1. 리뷰 반영 요약

외부 리뷰 8개 항목 중 6개 즉시 반영, 2개 지연 반영으로 확정하였다.

| # | 제안 | 판정 | 반영 시점 |
|---|---|---|---|
| 1 | 룰 SoT 백엔드 집중, 프론트 폴더명 변경 | ✅ 반영 | 즉시 |
| 2 | Canonical ↔ UI 스키마 분리 + schema_version | ✅ 반영 | 즉시 |
| 3 | Generate 3레벨 분리 | ⚠️ 함수 시그니처만 | 즉시 |
| 4 | Export 번들(zip) + manifest + run_meta | ✅ 반영 | 즉시 |
| 5 | Ruleset 버전/해시/스코프 + hash MVP부터 | ✅ 반영 | 즉시 |
| 6 | domain/infra/services 레이어 분리 | ⚠️ 경계 규칙만 | 나중에 |
| 7 | Docker SQLite 절대경로 + volume | ✅ 반영 | 즉시 |
| 8 | pyproject.toml, pre-commit, ruff | ✅ 반영 | 즉시 |

### 채택하지 않은 항목

| 리뷰 제안 | 사유 |
|---|---|
| `migrations/`를 `db/` 아래로 이동 | Alembic은 backend Python 환경에서 실행되어야 함 → `backend/alembic/` 유지 |
| `domain/` + `infra/` 레이어 분리 | 1인 MVP에서 4계층은 과잉 → `services/`에 경계 규칙만 적용 |
| `generate.py`를 3개 모듈로 분리 | 파일 1개 유지, 함수 시그니처 3개로만 분리 |

---

## 2. 프로젝트 디렉토리 구조 (확정)

```
pei/
├── frontend/                        # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── canvas/              # P&ID 캔버스 (ReactFlow)
│   │   │   ├── panels/              # 속성패널, 검증패널, 장비팔레트
│   │   │   └── common/              # 공통 UI 컴포넌트
│   │   ├── stores/                  # Zustand 상태관리
│   │   ├── services/                # API 클라이언트
│   │   ├── symbols/                 # SVG 심볼 라이브러리
│   │   ├── reference/               # ← (변경) 서버 캐시 참조 데이터
│   │   │   ├── isa-codes.ts         #   ISA 문자코드 캐시
│   │   │   ├── equipment-classes.ts #   장비분류 캐시
│   │   │   └── line-styles.ts       #   선종 스타일 캐시
│   │   ├── converters/              # ← (신규) Canonical ↔ UI 변환기
│   │   │   ├── to-canonical.ts
│   │   │   └── to-reactflow.ts
│   │   └── types/                   # TypeScript 타입 정의
│   │       ├── canonical.ts         #   Canonical Diagram 스키마
│   │       └── ui.ts                #   ReactFlow UI 스키마
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .eslintrc.cjs
│
├── backend/                         # Python FastAPI
│   ├── app/
│   │   ├── api/                     # 라우터 (HTTP 레이어만)
│   │   │   ├── rules.py             #   규칙 CRUD
│   │   │   ├── validate.py          #   검증 요청/응답
│   │   │   ├── generate.py          #   생성 요청/응답
│   │   │   ├── diagrams.py          #   도면 CRUD
│   │   │   └── export.py            #   번들 내보내기
│   │   ├── services/                # 비즈니스 로직 (유스케이스)
│   │   │   ├── validator.py         #   그래프 패턴 매칭 검증
│   │   │   ├── generator.py         #   generate_template()
│   │   │   │                        #   auto_repair()
│   │   │   │                        #   ai_assist()
│   │   │   ├── exporter.py          #   번들 ZIP 생성
│   │   │   └── seed_loader.py       #   시드 데이터 주입
│   │   ├── schemas/                 # ← (강화) Pydantic 스키마
│   │   │   ├── canonical.py         #   DiagramCanonical (domain schema)
│   │   │   ├── ui.py                #   DiagramUI (ReactFlow schema)
│   │   │   ├── converters.py        #   ui_to_canonical(), canonical_to_ui()
│   │   │   ├── rules.py             #   Rule, Ruleset 스키마
│   │   │   └── export.py            #   Manifest, RunMeta 스키마
│   │   ├── models/                  # SQLAlchemy ORM
│   │   │   ├── diagram.py           #   projects, diagrams 테이블
│   │   │   ├── ruleset.py           #   rulesets, rules 테이블
│   │   │   └── run.py               #   runs (검증 이력) 테이블
│   │   ├── core/
│   │   │   ├── config.py            #   설정 (환경변수)
│   │   │   └── database.py          #   DB 연결/세션
│   │   └── main.py
│   ├── alembic/                     # DB 마이그레이션
│   │   └── versions/
│   ├── alembic.ini
│   ├── pyproject.toml               # ← (변경) requirements.txt 대체
│   └── data/                        # ← (신규) SQLite DB 파일 위치
│       └── .gitkeep
│
├── db/
│   └── seeds/                       # 초기 규칙 데이터
│       ├── isa_letter_codes.json
│       ├── equipment_classes.json
│       ├── line_styles.json
│       ├── validation_rules.json
│       └── generation_rules.json
│
├── docs/                            # 프로젝트 문서
│   ├── architecture.md
│   ├── canonical-schema.md          # ← (신규) Canonical 스키마 명세
│   ├── rules-spec.md
│   └── api-spec.md
│
├── ops/                             # ← (변경) 운영/배포 분리
│   └── docker-compose.yml
│
├── .editorconfig                    # ← (신규)
├── .pre-commit-config.yaml          # ← (신규)
├── ruff.toml                        # ← (신규)
├── Makefile
└── README.md
```

---

## 3. 주요 변경 상세

### 3.1 Canonical ↔ UI 스키마 분리

ReactFlow에 종속되지 않는 도메인 스키마(Canonical)를 정의하고, UI 표현과 분리한다.

| 구분 | Canonical (Domain) | UI (ReactFlow) |
|---|---|---|
| 위치 | `backend/schemas/canonical.py` + `frontend/types/canonical.ts` | `frontend/types/ui.ts` |
| 역할 | 저장, 검증, 생성, 내보내기의 기준 | ReactFlow 렌더링 전용 |
| 라이브러리 의존 | 없음 (순수 데이터 구조) | ReactFlow 타입에 의존 |
| 버전 필드 | `canonical_schema_version: int` | `ui_schema_version: int` + `reactflow_version: string` |
| 저장 | DB에 저장 (`diagrams.canonical_json`) | 저장 안 함 (실시간 변환) |

변환 흐름:

```
사용자 편집 (ReactFlow UI)
    │
    ▼  to_canonical()
Canonical JSON ──→ 저장/검증/생성/내보내기
    │
    ▼  to_reactflow()
ReactFlow UI ──→ 화면 렌더링
```

ReactFlow를 다른 라이브러리로 교체할 때 `converters/`만 수정하면 된다.

### 3.2 Ruleset 버전 관리

모든 검증/생성 결과는 `ruleset_id` + `hash`로 추적한다.

| 필드 | 타입 | 설명 | MVP 필수 |
|---|---|---|---|
| id | UUID | 고유 식별자 | ✅ |
| name | string | 규칙셋 이름 (예: pei-default) | ✅ |
| version | integer | 순차 버전 (1, 2, 3...) | ✅ |
| hash | string | 내용 기반 SHA-256 해시 | ✅ |
| status | enum | active / draft / deprecated | ✅ (active만 사용) |
| scope | string | 적용 범위 (global / project-specific) | 나중에 |

검증 이력 저장:

```
runs 테이블:
  run_id          UUID
  diagram_id      UUID    → diagrams.id
  diagram_version int     → 도면 버전
  ruleset_id      UUID    → rulesets.id
  ruleset_hash    string  → 실행 시점의 해시 (스냅샷)
  result_json     JSONB   → 검증 결과
  created_at      timestamp
```

"도면 v3이 ruleset v1(hash=abc123)에서 통과했다"를 추적할 수 있다.

### 3.3 Export 번들 구조

내보내기는 단일 파일이 아닌 재현 가능한 패키지(ZIP)로 구성한다.

```
export_20250219_P101.zip
├── manifest.json            # 파일 목록 + 각 파일 SHA-256
├── run_meta.json            # 생성 시각, app version, git commit
├── diagram.json             # Canonical JSON
├── diagram.svg              # 벡터 도면
├── diagram.pdf              # 인쇄용 도면
├── validation_report.json   # 검증 결과 상세
├── ruleset_ref.json         # 적용된 규칙셋 버전 + 해시
└── deliverables/            # 산출물
    ├── equipment_list.xlsx
    ├── line_list.xlsx
    ├── valve_list.xlsx
    └── instrument_index.xlsx
```

### 3.4 Generator 함수 시그니처 (파일 1개, 엔트리 3개)

`generator.py` 내에 3개 함수를 명시적으로 분리한다.

```python
# backend/app/services/generator.py

def generate_template(
    canonical: DiagramCanonical,
    ruleset: Ruleset
) -> DiagramCanonical:
    """규칙/템플릿 기반 P&ID 초안 생성"""

def auto_repair(
    canonical: DiagramCanonical,
    validation_report: ValidationReport,
    ruleset: Ruleset
) -> DiagramCanonical:
    """검증 실패 항목을 룰 기반으로 자동 수정"""

def ai_assist(
    prompt_or_context: str,
    canonical: DiagramCanonical,
    ruleset: Ruleset
) -> DiagramPatch:
    """AI 기반 수정/생성 제안 (diff 형태)"""
```

### 3.5 services/ 경계 규칙 (domain 추출 대비)

1인 개발 MVP에서 별도 `domain/` 레이어는 두지 않되, 나중에 추출이 쉽도록 아래 규칙을 준수한다.

- **FastAPI 직접 참조 금지** — `services/` 내부에서 `Request`, `Depends`, `HTTPException` 등 FastAPI 객체를 import하지 않는다.
- **DB 세션 주입** — DB 세션은 함수 인자로 받는다. services 내부에서 직접 세션을 생성하지 않는다.
- **Pydantic I/O 고정** — 모든 services 함수의 입력/출력은 `schemas/`에 정의된 Pydantic 모델을 사용한다.

이 3가지만 지키면, 나중에 `services/validator.py` → `domain/validator.py`로 파일 이동만으로 분리 가능하다.

---

## 4. 기술 스택 (확정)

| 영역 | 기술 | 버전/비고 |
|---|---|---|
| **Frontend** | | |
| 프레임워크 | React 18 + TypeScript 5 | Vite 빌드 |
| 캔버스 | ReactFlow | 노드-엣지 그래프 최적화 |
| 상태관리 | Zustand | 보일러플레이트 최소 |
| 린트/포맷 | ESLint + Prettier | |
| **Backend** | | |
| 프레임워크 | FastAPI | Python 3.12, async |
| ORM | SQLAlchemy 2.0 | async 지원, 타입 힌트 |
| 마이그레이션 | Alembic | |
| 린트/포맷 | ruff | lint + format 통합 |
| 테스트 | pytest | |
| 타입체크 | mypy (선택) | 규모 커지면 도입 |
| **Database** | | |
| MVP | SQLite | `backend/data/pei.db` (절대경로) |
| SaaS 전환 | PostgreSQL 16 | JSONB 활용 |
| **DevOps** | | |
| 컨테이너 | Docker Compose | `ops/docker-compose.yml` |
| 코드 품질 | pre-commit (ruff + eslint) | 커밋 전 자동 검사 |
| 패키지 관리 | pyproject.toml | requirements.txt 대체 |

---

## 5. Docker Compose (수정)

```yaml
# ops/docker-compose.yml

services:
  frontend:
    build: ../frontend
    ports:
      - "5173:5173"                    # Vite 기본 포트
    depends_on: [backend]
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build: ../backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:////app/data/pei.db    # 절대경로
    volumes:
      - ../backend/data:/app/data      # SQLite 파일 명시적 마운트
      - ../db/seeds:/app/seeds          # 시드 데이터

  # SaaS 전환 시 활성화
  # postgres:
  #   image: postgres:16-alpine
  #   environment:
  #     POSTGRES_DB: pei
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - pgdata:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"
```

---

## 6. Makefile 표준 명령어

```makefile
# 개발 환경
make dev            # frontend + backend 동시 실행
make dev-front      # Vite dev server (5173)
make dev-back       # uvicorn --reload (8000)

# 코드 품질
make fmt            # ruff format + prettier
make lint           # ruff check + eslint
make test           # pytest + vitest

# DB
make db-migrate     # alembic upgrade head
make db-seed        # 시드 데이터 주입
make db-reset       # drop + migrate + seed

# Docker
make up             # docker compose up -d
make down           # docker compose down
```
