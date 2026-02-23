# PEI 백엔드 API 설계서

---

## 1. API 개요

| 항목 | 값 |
|---|---|
| Base URL | `http://localhost:8000/api/v1` |
| 프레임워크 | FastAPI (Python 3.12) |
| 인증 | MVP: 없음 → SaaS: JWT Bearer Token |
| 응답 형식 | JSON |
| 에러 형식 | `{ "detail": "message", "code": "ERROR_CODE" }` |
| API 문서 | `/docs` (Swagger) / `/redoc` (ReDoc) |

---

## 2. 엔드포인트 목록

### 2.1 Projects

| Method | Path | 설명 |
|---|---|---|
| POST | `/projects` | 프로젝트 생성 |
| GET | `/projects` | 프로젝트 목록 조회 |
| GET | `/projects/{id}` | 프로젝트 상세 조회 |
| PATCH | `/projects/{id}` | 프로젝트 수정 |
| DELETE | `/projects/{id}` | 프로젝트 삭제 |

### 2.2 Diagrams

| Method | Path | 설명 |
|---|---|---|
| POST | `/projects/{project_id}/diagrams` | 도면 생성 |
| GET | `/projects/{project_id}/diagrams` | 도면 목록 조회 |
| GET | `/diagrams/{id}` | 도면 상세 조회 (canonical_json 포함) |
| PUT | `/diagrams/{id}` | 도면 전체 업데이트 (새 버전 생성) |
| PATCH | `/diagrams/{id}` | 도면 부분 수정 (메타데이터만) |
| DELETE | `/diagrams/{id}` | 도면 삭제 |
| GET | `/diagrams/{id}/versions` | 도면 버전 이력 조회 |

### 2.3 Rulesets

| Method | Path | 설명 |
|---|---|---|
| GET | `/rulesets` | 규칙셋 목록 조회 |
| GET | `/rulesets/{id}` | 규칙셋 상세 (규칙 포함) |
| GET | `/rulesets/active` | 현재 활성 규칙셋 조회 |
| POST | `/rulesets` | 규칙셋 생성 (새 버전) |
| PATCH | `/rulesets/{id}` | 규칙셋 상태 변경 (active/deprecated) |

### 2.4 Rules (CRUD)

| Method | Path | 설명 |
|---|---|---|
| GET | `/rulesets/{ruleset_id}/rules` | 규칙 목록 (필터링/페이지네이션) |
| GET | `/rules/{id}` | 규칙 상세 조회 |
| POST | `/rulesets/{ruleset_id}/rules` | 규칙 추가 |
| PUT | `/rules/{id}` | 규칙 전체 수정 |
| PATCH | `/rules/{id}` | 규칙 부분 수정 (enabled 토글 등) |
| DELETE | `/rules/{id}` | 규칙 삭제 |
| POST | `/rulesets/{ruleset_id}/rules/bulk` | 규칙 일괄 추가 (시드 데이터용) |

### 2.5 Validate (검증)

| Method | Path | 설명 |
|---|---|---|
| POST | `/validate` | 도면 검증 실행 |
| POST | `/validate/quick` | 단일 노드/엣지 빠른 검증 |
| GET | `/runs/{diagram_id}` | 도면의 검증 이력 조회 |
| GET | `/runs/{diagram_id}/{run_id}` | 특정 검증 결과 상세 |

### 2.6 Generate (생성)

| Method | Path | 설명 |
|---|---|---|
| POST | `/generate/template` | 규칙 기반 P&ID 초안 생성 |
| POST | `/generate/auto-repair` | 검증 실패 자동 수정 |
| POST | `/generate/ai-assist` | AI 기반 수정 제안 (Phase 3) |

### 2.7 Export (내보내기)

| Method | Path | 설명 |
|---|---|---|
| POST | `/export/bundle` | 전체 번들 ZIP 내보내기 |
| POST | `/export/deliverables` | 산출물만 내보내기 (장비리스트 등) |
| POST | `/export/svg` | SVG 도면만 내보내기 |
| POST | `/export/pdf` | PDF 도면만 내보내기 |

### 2.8 Reference (참조 데이터)

| Method | Path | 설명 |
|---|---|---|
| GET | `/reference/isa-codes` | ISA 문자코드 전체 (프론트 캐시용) |
| GET | `/reference/equipment-classes` | PIP 장비분류 전체 |
| GET | `/reference/line-styles` | 선종 스타일 전체 |
| GET | `/reference/symbols` | 심볼 목록 (타입별 필터링) |

---

## 3. 상세 스키마

### 3.1 Projects

**POST /projects — Request**

```json
{
  "name": "30K PLA Pellet Plant",
  "description": "30,000 TPA PLA 펠릿 생산 플랜트"
}
```

**Response 201**

```json
{
  "id": "proj-uuid-001",
  "name": "30K PLA Pellet Plant",
  "description": "30,000 TPA PLA 펠릿 생산 플랜트",
  "created_at": "2025-02-19T10:00:00Z",
  "updated_at": "2025-02-19T10:00:00Z"
}
```

### 3.2 Diagrams

**POST /projects/{project_id}/diagrams — Request**

```json
{
  "name": "PID-001",
  "diagram_type": "PID",
  "canonical_json": {
    "canonical_schema_version": 1,
    "metadata": {
      "area": "100",
      "revision": "A"
    },
    "nodes": [],
    "edges": [],
    "signal_lines": []
  }
}
```

**PUT /diagrams/{id} — Request**

전체 canonical_json을 교체한다. 자동으로 version이 +1 증가한다.

```json
{
  "canonical_json": { "...전체 canonical 데이터..." },
  "change_description": "R-101 추가, 제어루프 TIC-101 추가"
}
```

**GET /diagrams/{id} — Response 200**

```json
{
  "id": "diag-uuid-001",
  "project_id": "proj-uuid-001",
  "name": "PID-001",
  "diagram_type": "PID",
  "version": 3,
  "canonical_schema_version": 1,
  "status": "draft",
  "canonical_json": { "..." },
  "created_at": "2025-02-19T10:00:00Z",
  "updated_at": "2025-02-19T11:30:00Z"
}
```

### 3.3 Rules

**GET /rulesets/{ruleset_id}/rules — Query Parameters**

| Param | Type | 설명 |
|---|---|---|
| `category` | string | 필터: symbol, tag, instrument, piping, valve, equipment, safety, layout, completeness, process |
| `kind` | string | 필터: lookup, validate, generate |
| `scope` | string | 필터: PFD, PID, both |
| `severity` | string | 필터: error, warning, info |
| `layer` | string | 필터: L1 ~ L5 |
| `enabled` | boolean | 필터: true/false |
| `search` | string | 이름/설명 검색 |
| `page` | integer | 페이지 번호 (기본 1) |
| `per_page` | integer | 페이지당 수 (기본 50, 최대 200) |

**Response 200**

```json
{
  "items": [
    {
      "id": "rule-uuid-001",
      "ruleset_id": "rs-uuid-001",
      "code": "VAL-EQP-001",
      "category": "equipment",
      "kind": "validate",
      "scope": "PID",
      "severity": "error",
      "layer": "L2",
      "name_ko": "펌프 토출측 체크밸브 필수",
      "name_en": "Check valve required at pump discharge",
      "description": "원심펌프 또는 왕복동펌프의 토출측에는 역류 방지를 위한 체크밸브가 반드시 설치되어야 한다.",
      "condition_json": {
        "match": "node",
        "where": { "type": "equipment", "subtype": "pump" },
        "check": {
          "downstream_edge": {
            "has_node": { "type": "valve", "subtype": "check_valve" },
            "max_distance": 2
          }
        }
      },
      "message_template": "{tag}의 토출측에 체크밸브가 없습니다.",
      "reference": "설계 관행, API RP 14C",
      "priority": 100,
      "is_overridable": false,
      "enabled": true
    }
  ],
  "total": 110,
  "page": 1,
  "per_page": 50
}
```

**POST /rulesets/{ruleset_id}/rules — Request**

```json
{
  "code": "VAL-EQP-016",
  "category": "equipment",
  "kind": "validate",
  "scope": "PID",
  "severity": "warning",
  "layer": "L2",
  "name_ko": "고온 펌프 냉각 배관 필수",
  "condition_json": {
    "match": "node",
    "where": {
      "type": "equipment",
      "subtype": "pump",
      "properties.design_temperature": { "$gt": 200 }
    },
    "check": {
      "connected_to": {
        "has_node": { "type": "utility", "subtype": "cooling_water" }
      }
    }
  },
  "message_template": "{tag}은 설계온도 {design_temperature}°C로, 냉각 배관이 필요합니다.",
  "reference": "설계 관행"
}
```

**POST /rulesets/{ruleset_id}/rules/bulk — Request**

```json
{
  "rules": [
    { "code": "LKP-ISA-001", "category": "instrument", "kind": "lookup", "..." : "..." },
    { "code": "LKP-ISA-002", "..." : "..." }
  ]
}
```

**Response 201**

```json
{
  "created": 26,
  "skipped": 0,
  "errors": []
}
```

### 3.4 Validate

**POST /validate — Request**

```json
{
  "diagram_id": "diag-uuid-001",
  "ruleset_id": "rs-uuid-001",
  "options": {
    "severity_filter": ["error", "warning"],
    "category_filter": [],
    "stop_on_first_error": false
  }
}
```

`diagram_id`가 없으면 `canonical_json`을 직접 전달할 수도 있다 (저장 전 검증):

```json
{
  "canonical_json": { "..." },
  "ruleset_id": "rs-uuid-001"
}
```

**Response 200**

```json
{
  "run_id": "run-uuid-001",
  "diagram_id": "diag-uuid-001",
  "diagram_version": 3,
  "ruleset_id": "rs-uuid-001",
  "ruleset_hash": "sha256:abc123...",
  "passed": false,
  "summary": {
    "total_rules_checked": 85,
    "passed": 79,
    "errors": 4,
    "warnings": 2,
    "info": 0
  },
  "violations": [
    {
      "rule_code": "VAL-EQP-001",
      "severity": "error",
      "category": "equipment",
      "message": "P-101의 토출측에 체크밸브가 없습니다.",
      "node_id": "node-005",
      "node_tag": "P-101",
      "suggestion": "P-101 토출측에 체크밸브를 추가하세요.",
      "reference": "설계 관행, API RP 14C",
      "auto_repairable": true
    },
    {
      "rule_code": "VAL-EQP-003",
      "severity": "error",
      "category": "equipment",
      "message": "V-201에 PSV가 연결되어 있지 않습니다.",
      "node_id": "node-012",
      "node_tag": "V-201",
      "suggestion": "V-201에 PSV를 추가하세요.",
      "reference": "ASME BPVC VIII, KOSHA PSMD",
      "auto_repairable": true
    },
    {
      "rule_code": "VAL-PIP-002",
      "severity": "error",
      "category": "piping",
      "message": "edge-007에 라인넘버가 없습니다.",
      "node_id": null,
      "edge_id": "edge-007",
      "suggestion": "라인넘버를 입력하세요.",
      "auto_repairable": false
    },
    {
      "rule_code": "VAL-INS-001",
      "severity": "error",
      "category": "instrument",
      "message": "제어루프 TIC-101에 최종 제어요소(밸브)가 없습니다.",
      "node_id": "node-020",
      "node_tag": "TIC-101",
      "suggestion": "TIC-101 루프에 제어밸브(TV-101)를 추가하세요.",
      "auto_repairable": true
    },
    {
      "rule_code": "VAL-EQP-006",
      "severity": "warning",
      "category": "equipment",
      "message": "E-101에 벤트 밸브가 없습니다.",
      "node_id": "node-008",
      "node_tag": "E-101",
      "suggestion": "E-101 상부에 벤트 밸브를 추가하세요.",
      "auto_repairable": true
    },
    {
      "rule_code": "VAL-CMP-005",
      "severity": "warning",
      "category": "completeness",
      "message": "node-025는 어떤 배관과도 연결되어 있지 않습니다.",
      "node_id": "node-025",
      "node_tag": "FI-103",
      "suggestion": "미연결 노드를 삭제하거나 배관을 연결하세요.",
      "auto_repairable": false
    }
  ],
  "created_at": "2025-02-19T11:35:00Z"
}
```

**POST /validate/quick — Request**

단일 노드 또는 엣지를 빠르게 검증한다. 캔버스에서 실시간 피드백용.

```json
{
  "canonical_json": { "..." },
  "target": {
    "type": "node",
    "id": "node-005"
  },
  "ruleset_id": "rs-uuid-001"
}
```

**Response 200**

```json
{
  "target_id": "node-005",
  "violations": [
    {
      "rule_code": "VAL-EQP-001",
      "severity": "error",
      "message": "P-101의 토출측에 체크밸브가 없습니다.",
      "auto_repairable": true
    }
  ]
}
```

### 3.5 Generate

**POST /generate/template — Request**

```json
{
  "canonical_json": {
    "canonical_schema_version": 1,
    "nodes": [
      {
        "id": "node-001",
        "type": "equipment",
        "subtype": "pump",
        "tag": "P-101",
        "position": { "x": 400, "y": 300 }
      }
    ],
    "edges": []
  },
  "ruleset_id": "rs-uuid-001"
}
```

**Response 200**

```json
{
  "canonical_json": {
    "canonical_schema_version": 1,
    "nodes": [
      { "id": "node-001", "type": "equipment", "subtype": "pump", "tag": "P-101", "position": { "x": 400, "y": 300 } },
      { "id": "gen-001", "type": "valve", "subtype": "block_valve", "tag": "HV-101A", "position": { "x": 280, "y": 300 }, "_generated": true },
      { "id": "gen-002", "type": "valve", "subtype": "check_valve", "tag": "CV-101", "position": { "x": 520, "y": 300 }, "_generated": true },
      { "id": "gen-003", "type": "valve", "subtype": "block_valve", "tag": "HV-101B", "position": { "x": 640, "y": 300 }, "_generated": true }
    ],
    "edges": [
      { "id": "gen-e001", "from_node": "gen-001", "to_node": "node-001", "_generated": true },
      { "id": "gen-e002", "from_node": "node-001", "to_node": "gen-002", "_generated": true },
      { "id": "gen-e003", "from_node": "gen-002", "to_node": "gen-003", "_generated": true }
    ]
  },
  "applied_rules": [
    { "code": "GEN-EQP-001", "description": "체크밸브 자동 추가", "affected_nodes": ["gen-002"] },
    { "code": "GEN-EQP-002", "description": "차단밸브 자동 추가", "affected_nodes": ["gen-001", "gen-003"] }
  ]
}
```

**POST /generate/auto-repair — Request**

```json
{
  "diagram_id": "diag-uuid-001",
  "run_id": "run-uuid-001",
  "repair_targets": ["VAL-EQP-001", "VAL-EQP-003"],
  "ruleset_id": "rs-uuid-001"
}
```

특정 violation만 수정하거나, `repair_targets`를 생략하면 `auto_repairable: true`인 전체 항목을 수정한다.

**Response 200**

```json
{
  "canonical_json": { "...수정된 전체 canonical..." },
  "repairs": [
    {
      "rule_code": "VAL-EQP-001",
      "action": "P-101 토출측에 체크밸브 CV-101 추가",
      "added_nodes": ["gen-cv-001"],
      "added_edges": ["gen-e-001"]
    },
    {
      "rule_code": "VAL-EQP-003",
      "action": "V-201에 PSV-201 + 입구 차단밸브(CSO) 추가",
      "added_nodes": ["gen-psv-001", "gen-bv-001"],
      "added_edges": ["gen-e-002", "gen-e-003"]
    }
  ],
  "remaining_violations": 2
}
```

### 3.6 Export

**POST /export/bundle — Request**

```json
{
  "diagram_id": "diag-uuid-001",
  "run_id": "run-uuid-001",
  "include_deliverables": true,
  "deliverables": ["equipment_list", "line_list", "valve_list", "instrument_index"]
}
```

**Response 200** — `Content-Type: application/zip`

ZIP 파일 직접 반환. 파일명: `PEI_PID-001_v3_20250219.zip`

### 3.7 Reference

**GET /reference/isa-codes — Response 200**

```json
{
  "version": "2025.1",
  "first_letters": [
    { "letter": "A", "measured_variable": "Analysis", "measured_variable_ko": "분석" },
    { "letter": "F", "measured_variable": "Flow Rate", "measured_variable_ko": "유량" },
    { "letter": "L", "measured_variable": "Level", "measured_variable_ko": "레벨(액위)" },
    { "letter": "P", "measured_variable": "Pressure/Vacuum", "measured_variable_ko": "압력/진공" },
    { "letter": "T", "measured_variable": "Temperature", "measured_variable_ko": "온도" }
  ],
  "succeeding_letters": [
    { "letter": "A", "function": "Alarm", "function_ko": "알람" },
    { "letter": "C", "function": "Control", "function_ko": "제어" },
    { "letter": "I", "function": "Indicate", "function_ko": "지시" }
  ]
}
```

프론트는 이 응답을 `reference/isa-codes.ts`에 캐시하여 오프라인에서도 동작한다.

---

## 4. 검증 엔진 내부 설계

### 4.1 검증 흐름

```
canonical_json 입력
    │
    ▼
[1] 그래프 구축
    nodes → 노드 맵 (id → node)
    edges → 인접 리스트 (upstream/downstream)
    │
    ▼
[2] 규칙 로딩
    ruleset_id로 활성 규칙 조회
    scope 필터 (PFD/PID)
    enabled 필터
    │
    ▼
[3] 규칙별 평가
    각 규칙의 condition_json을 그래프에 대해 평가
    ├── lookup: 스킵 (검증 대상 아님)
    ├── validate: match → where → check
    └── generate: 스킵 (생성 시에만 사용)
    │
    ▼
[4] 결과 집계
    violations 목록 생성
    passed/failed 판정
    runs 테이블에 저장
```

### 4.2 그래프 패턴 매칭 엔진

condition_json의 `check` 필드를 평가하는 핵심 로직:

```python
# backend/app/services/validator.py

from app.schemas.canonical import DiagramCanonical
from app.schemas.rules import Rule, Ruleset, ValidationReport

def validate(
    canonical: DiagramCanonical,
    ruleset: Ruleset,
    options: ValidateOptions | None = None
) -> ValidationReport:
    """전체 도면 검증"""
    graph = build_graph(canonical)
    rules = filter_rules(ruleset, canonical.diagram_type, options)
    violations = []

    for rule in rules:
        if rule.kind != "validate":
            continue
        matched_nodes = match_nodes(graph, rule.condition_json["where"])
        for node in matched_nodes:
            if not check_condition(graph, node, rule.condition_json["check"]):
                violations.append(build_violation(rule, node))

    return build_report(canonical, ruleset, violations)


def validate_quick(
    canonical: DiagramCanonical,
    target_id: str,
    ruleset: Ruleset
) -> list[Violation]:
    """단일 노드/엣지 빠른 검증"""
    graph = build_graph(canonical)
    target = graph.get_node(target_id)
    rules = filter_rules_for_node(ruleset, target)
    violations = []

    for rule in rules:
        if not check_condition(graph, target, rule.condition_json["check"]):
            violations.append(build_violation(rule, target))

    return violations
```

### 4.3 check 연산자

condition_json의 `check` 필드에서 사용 가능한 연산자:

| 연산자 | 설명 | 예시 |
|---|---|---|
| `downstream_edge.has_node` | 하류에 특정 노드 존재 여부 | 펌프 → 체크밸브 |
| `upstream_edge.has_node` | 상류에 특정 노드 존재 여부 | PSV ← 차단밸브 |
| `connected_to.has_node` | 방향 무관 연결 여부 | 용기 ↔ 벤트밸브 |
| `max_distance` | 최대 허용 홉 수 | 2홉 이내 |
| `has_property` | 속성 존재 여부 | tag ≠ null |
| `property_matches` | 속성 정규식 매칭 | tag matches `P-\d{3}` |
| `property_compare` | 속성 비교 (`$gt`, `$lt`, `$eq`) | design_T > 200 |
| `count` | 연결 노드 수 | drain_valve count ≥ 1 |
| `is_unique` | 값 유일성 | tag is unique |
| `loop_complete` | 제어루프 완결성 | sensor + controller + final_element |
| `not_exists` | 특정 노드 부재 확인 | PFD에 drain_valve 없어야 |

MVP에서는 `downstream_edge.has_node`, `has_property`, `property_matches`, `is_unique`, `count`를 먼저 구현하고, 나머지는 규칙 추가에 따라 확장한다.

---

## 5. 에러 코드

| HTTP | Code | 설명 |
|---|---|---|
| 400 | `INVALID_CANONICAL` | canonical_json 스키마 유효성 실패 |
| 400 | `INVALID_RULE_CONDITION` | condition_json 구문 오류 |
| 400 | `SCHEMA_VERSION_MISMATCH` | canonical_schema_version 불일치 |
| 404 | `PROJECT_NOT_FOUND` | 프로젝트 미존재 |
| 404 | `DIAGRAM_NOT_FOUND` | 도면 미존재 |
| 404 | `RULESET_NOT_FOUND` | 규칙셋 미존재 |
| 404 | `RULE_NOT_FOUND` | 규칙 미존재 |
| 404 | `RUN_NOT_FOUND` | 검증 이력 미존재 |
| 409 | `RULE_CODE_DUPLICATE` | 규칙 코드 중복 |
| 409 | `TAG_DUPLICATE` | 태그 번호 중복 |
| 422 | `VALIDATION_FAILED` | 검증은 성공했으나 위반 존재 (정상 응답) |

---

## 6. MVP 구현 우선순위

| 순서 | 엔드포인트 | 이유 |
|---|---|---|
| 1 | `GET/POST /reference/*` | 프론트 캐시 데이터 제공, 가장 단순 |
| 2 | `POST/GET /rulesets`, `POST/GET /rules`, `POST /rules/bulk` | 시드 데이터 주입 + 규칙 관리 |
| 3 | `POST/GET /projects`, `POST/GET /diagrams` | 도면 저장/로드 |
| 4 | `POST /validate` | 핵심 기능: 검증 실행 |
| 5 | `POST /validate/quick` | 실시간 캔버스 피드백 |
| 6 | `POST /generate/template` | 자동 배치 |
| 7 | `POST /generate/auto-repair` | 자동 수정 |
| 8 | `POST /export/bundle` | 번들 내보내기 |

1~5번이 MVP 핵심이며, 6~8번은 MVP 이후 확장이다.
