# PEI 규격 DB 스키마 + 핵심 규칙 100건

## 1. 데이터베이스 스키마 (SQLite → PostgreSQL 호환)

### 1.1 ERD 개요

```
projects ──1:N──→ diagrams ──1:N──→ runs ←──N:1── rulesets ──1:N──→ rules
```

### 1.2 테이블 정의

#### projects

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | TEXT (UUID) | PK |
| name | TEXT NOT NULL | 프로젝트명 |
| description | TEXT | 설명 |
| created_at | TIMESTAMP | 생성일시 |
| updated_at | TIMESTAMP | 수정일시 |

#### diagrams

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | TEXT (UUID) | PK |
| project_id | TEXT | FK → projects.id |
| name | TEXT NOT NULL | 도면명 (예: PID-001) |
| diagram_type | TEXT NOT NULL | 'PFD' \| 'PID' \| 'BFD' \| 'UFD' |
| version | INTEGER NOT NULL | 도면 버전 (1, 2, 3...) |
| canonical_json | JSON NOT NULL | Canonical 스키마 데이터 |
| canonical_schema_version | INTEGER NOT NULL DEFAULT 1 | 스키마 버전 |
| status | TEXT DEFAULT 'draft' | 'draft' \| 'review' \| 'approved' |
| created_at | TIMESTAMP | 생성일시 |
| updated_at | TIMESTAMP | 수정일시 |

#### rulesets

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | TEXT (UUID) | PK |
| name | TEXT NOT NULL | 규칙셋명 (예: pei-default) |
| version | INTEGER NOT NULL | 순차 버전 |
| hash | TEXT NOT NULL | 내용 기반 SHA-256 |
| status | TEXT DEFAULT 'active' | 'active' \| 'draft' \| 'deprecated' |
| description | TEXT | 설명 |
| created_at | TIMESTAMP | 생성일시 |
| UNIQUE(name, version) | | 이름+버전 중복 방지 |

#### rules

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | TEXT (UUID) | PK |
| ruleset_id | TEXT NOT NULL | FK → rulesets.id |
| code | TEXT NOT NULL UNIQUE | 규칙 코드 (예: VAL-PID-001) |
| category | TEXT NOT NULL | 분류 (아래 참조) |
| kind | TEXT NOT NULL | 'lookup' \| 'validate' \| 'generate' |
| scope | TEXT NOT NULL | 'PFD' \| 'PID' \| 'both' |
| severity | TEXT | 'error' \| 'warning' \| 'info' (validate만) |
| name_ko | TEXT NOT NULL | 규칙명 (한국어) |
| name_en | TEXT | 규칙명 (영어) |
| description | TEXT | 상세 설명 |
| condition_json | JSON | 조건 (validate/generate용) |
| action_json | JSON | 액션 (generate용) |
| message_template | TEXT | 위반 시 메시지 템플릿 |
| reference | TEXT | 규격 출처 (예: ISA-5.1 §4.3) |
| layer | TEXT NOT NULL | 'L1' ~ 'L5' (규칙 계층) |
| priority | INTEGER DEFAULT 100 | 충돌 시 우선순위 (낮을수록 우선) |
| is_overridable | BOOLEAN DEFAULT false | 프로젝트별 오버라이드 가능 여부 |
| enabled | BOOLEAN DEFAULT true | 활성화 여부 |

#### runs

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | TEXT (UUID) | PK |
| diagram_id | TEXT NOT NULL | FK → diagrams.id |
| diagram_version | INTEGER NOT NULL | 검증 시점 도면 버전 |
| ruleset_id | TEXT NOT NULL | FK → rulesets.id |
| ruleset_hash | TEXT NOT NULL | 실행 시점 해시 (스냅샷) |
| result_json | JSON NOT NULL | 검증 결과 상세 |
| passed | BOOLEAN NOT NULL | 전체 통과 여부 |
| error_count | INTEGER DEFAULT 0 | error 수 |
| warning_count | INTEGER DEFAULT 0 | warning 수 |
| created_at | TIMESTAMP | 실행일시 |

---

### 1.3 규칙 카테고리 분류

| category 값 | 설명 | 예시 |
|---|---|---|
| `symbol` | 심볼 매핑/표현 | ISA 계기 심볼, 장비 심볼 |
| `tag` | 태그/넘버링 | 장비 태그, 라인넘버, 계기 태그 |
| `instrument` | 계장 규칙 | 문자코드, 제어루프 |
| `piping` | 배관 규칙 | 선종, 라인넘버 형식 |
| `valve` | 밸브 규칙 | 필수 밸브, 밸브 배치 |
| `equipment` | 장비 규칙 | 필수 부속, 장비분류 |
| `safety` | 안전 규칙 | PSV, SIS |
| `layout` | 배치/표현 | 도면 흐름, 심볼 위치 |
| `completeness` | 완결성 | 루프 구성, 필수 항목 |
| `process` | 공정 특화 | PLA, Compound 등 |

### 1.4 condition_json / action_json 구조

```json
// validate 예시: "펌프 토출측에 체크밸브 필수"
{
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
  "message_template": "{tag}의 토출측에 체크밸브가 없습니다."
}

// generate 예시: "펌프 배치 시 체크밸브 자동 추가"
{
  "condition_json": {
    "trigger": "node_placed",
    "where": { "type": "equipment", "subtype": "pump" }
  },
  "action_json": {
    "add_node": {
      "type": "valve",
      "subtype": "check_valve",
      "position": "downstream",
      "offset": { "x": 120, "y": 0 }
    },
    "add_edge": {
      "from": "$trigger_node.discharge",
      "to": "$new_node.inlet"
    }
  }
}

// lookup 예시: ISA 문자코드
{
  "condition_json": {
    "letter": "F",
    "position": "first"
  },
  "action_json": {
    "measured_variable": "Flow Rate",
    "measured_variable_ko": "유량"
  }
}
```

---

## 2. Canonical Diagram 스키마

```json
{
  "canonical_schema_version": 1,
  "id": "uuid",
  "name": "PID-001",
  "diagram_type": "PID",
  "version": 1,
  "metadata": {
    "project": "30K PLA Pellet Plant",
    "area": "100",
    "revision": "A",
    "design_pressure_unit": "barg",
    "design_temp_unit": "°C"
  },
  "nodes": [
    {
      "id": "node-001",
      "type": "equipment",
      "subtype": "reactor",
      "tag": "R-101",
      "name": "Polymerization Reactor",
      "position": { "x": 400, "y": 300 },
      "properties": {
        "design_pressure": 5.0,
        "design_temperature": 220,
        "material": "SS316L",
        "capacity": "30 m³"
      },
      "nozzles": [
        { "id": "N1", "name": "Feed Inlet", "size": "4\"", "rating": "150#" },
        { "id": "N2", "name": "Product Outlet", "size": "6\"", "rating": "150#" },
        { "id": "N3", "name": "N2 Inlet", "size": "2\"", "rating": "150#" }
      ]
    },
    {
      "id": "node-002",
      "type": "valve",
      "subtype": "check_valve",
      "tag": "CV-101",
      "position": { "x": 550, "y": 300 },
      "properties": {
        "size": "6\"",
        "rating": "150#"
      }
    },
    {
      "id": "node-003",
      "type": "instrument",
      "subtype": "indicator_controller",
      "tag": "TIC-101",
      "position": { "x": 400, "y": 200 },
      "properties": {
        "measured_variable": "temperature",
        "range": "0-300 °C",
        "location": "field"
      }
    }
  ],
  "edges": [
    {
      "id": "edge-001",
      "from_node": "node-001",
      "from_port": "N2",
      "to_node": "node-002",
      "to_port": "inlet",
      "line_number": "6\"-PLA-001-A1A",
      "properties": {
        "size": "6\"",
        "spec": "A1A",
        "insulation": "H",
        "fluid": "PLA polymer"
      },
      "waypoints": []
    }
  ],
  "signal_lines": [
    {
      "id": "sig-001",
      "from_node": "node-003",
      "to_node": "node-001",
      "signal_type": "electrical",
      "description": "Temperature control signal to reactor"
    }
  ]
}
```

---

## 3. 핵심 규칙 100건 시드 데이터

### 3.1 Lookup — ISA 문자코드 (26건)

| code | letter | position | measured_variable | measured_variable_ko |
|---|---|---|---|---|
| LKP-ISA-001 | A | first | Analysis | 분석 |
| LKP-ISA-002 | B | first | Burner/Combustion | 연소 |
| LKP-ISA-003 | C | first | Conductivity | 전도도 |
| LKP-ISA-004 | D | first | Density/Specific Gravity | 밀도/비중 |
| LKP-ISA-005 | E | first | Voltage | 전압 |
| LKP-ISA-006 | F | first | Flow Rate | 유량 |
| LKP-ISA-007 | G | first | Gauging/Position | 위치/게이지 |
| LKP-ISA-008 | H | first | Hand (Manual) | 수동 |
| LKP-ISA-009 | I | succeeding | Indicate | 지시 |
| LKP-ISA-010 | J | first | Power | 전력 |
| LKP-ISA-011 | K | first | Time/Schedule | 시간 |
| LKP-ISA-012 | L | first | Level | 레벨(액위) |
| LKP-ISA-013 | M | first | Moisture/Humidity | 수분/습도 |
| LKP-ISA-014 | N | first | User's Choice | 사용자 정의 |
| LKP-ISA-015 | O | first | User's Choice | 사용자 정의 |
| LKP-ISA-016 | P | first | Pressure/Vacuum | 압력/진공 |
| LKP-ISA-017 | Q | first | Quantity/Event | 수량/이벤트 |
| LKP-ISA-018 | R | succeeding | Record | 기록 |
| LKP-ISA-019 | S | first | Speed/Frequency | 속도/주파수 |
| LKP-ISA-020 | T | first | Temperature | 온도 |
| LKP-ISA-021 | U | first | Multivariable | 다변수 |
| LKP-ISA-022 | V | first | Vibration | 진동 |
| LKP-ISA-023 | W | first | Weight/Force | 중량/힘 |
| LKP-ISA-024 | X | first | Unclassified | 미분류 |
| LKP-ISA-025 | Y | succeeding | Relay/Compute | 릴레이/연산 |
| LKP-ISA-026 | Z | first | Position/Dimension | 위치/치수 |

> reference: ISA-5.1 Table 4.1, scope: both, layer: L1

### 3.2 Lookup — ISA 기능문자 (12건)

| code | letter | position | function | function_ko |
|---|---|---|---|---|
| LKP-ISA-027 | A | succeeding | Alarm | 알람 |
| LKP-ISA-028 | C | succeeding | Control | 제어 |
| LKP-ISA-029 | E | succeeding | Sensor/Element | 검출기/소자 |
| LKP-ISA-030 | H | succeeding | High | 상한 |
| LKP-ISA-031 | I | succeeding | Indicate | 지시 |
| LKP-ISA-032 | L | succeeding | Low / Light | 하한 / 경보등 |
| LKP-ISA-033 | R | succeeding | Record | 기록 |
| LKP-ISA-034 | S | succeeding | Switch | 스위치 |
| LKP-ISA-035 | T | succeeding | Transmit | 전송 |
| LKP-ISA-036 | V | succeeding | Valve/Damper | 밸브/댐퍼 |
| LKP-ISA-037 | Y | succeeding | Relay/Compute | 릴레이/연산 |
| LKP-ISA-038 | Z | succeeding | Driver/Actuator | 구동기 |

> reference: ISA-5.1 Table 4.1, scope: both, layer: L1

### 3.3 Lookup — PIP 장비분류 코드 (12건)

| code | class_letter | equipment_class | equipment_class_ko | examples |
|---|---|---|---|---|
| LKP-PIP-001 | A | Heat Transfer Equipment | 열교환 장비 | Shell & Tube HX, Plate HX, Air Cooler |
| LKP-PIP-002 | B | Boilers & Fired Heaters | 보일러/가열로 | Process Heater, Waste Heat Boiler |
| LKP-PIP-003 | C | Columns/Towers | 탑/칼럼 | Distillation, Absorber, Stripper |
| LKP-PIP-004 | D | Dryers | 건조기 | Rotary, Spray, Fluid Bed |
| LKP-PIP-005 | E | Electrical Equipment | 전기 장비 | Transformer, Motor, Switchgear |
| LKP-PIP-006 | F | Solids Handling | 고체 처리 | Conveyor, Feeder, Crusher |
| LKP-PIP-007 | G | Gas Handling | 가스 처리 | Compressor, Blower, Vacuum Pump |
| LKP-PIP-008 | J | Liquid Handling | 액체 처리 | Centrifugal Pump, Metering Pump |
| LKP-PIP-009 | L | Reactors | 반응기 | CSTR, Plug Flow, Batch |
| LKP-PIP-010 | R | Pressure Vessels | 압력용기 | Drum, Separator, Accumulator |
| LKP-PIP-011 | T | Tanks/Storage | 저장탱크 | Atmospheric, Cone Roof, Silo |
| LKP-PIP-012 | V | Packaged Equipment | 패키지 장비 | Package Boiler, Chiller Unit |

> reference: PIP PIC001 Table 1, scope: both, layer: L1

### 3.4 Validate — 필수 요소 규칙 (15건)

| code | name_ko | severity | scope | condition 요약 |
|---|---|---|---|---|
| VAL-EQP-001 | 펌프 토출측 체크밸브 필수 | error | PID | pump.discharge → check_valve 존재 |
| VAL-EQP-002 | 펌프 흡입/토출측 차단밸브 필수 | error | PID | pump.suction/discharge → block_valve 존재 |
| VAL-EQP-003 | 압력용기에 PSV 필수 | error | PID | pressure_vessel → PSV 연결 존재 |
| VAL-EQP-004 | PSV 입구측 차단밸브 CSO 표기 | warning | PID | PSV 상류 block_valve → CSO(Car Sealed Open) |
| VAL-EQP-005 | 원심펌프 최소유량 바이패스 라인 | warning | PID | centrifugal_pump → min_flow_bypass 존재 |
| VAL-EQP-006 | 열교환기 벤트/드레인 밸브 필수 | error | PID | heat_exchanger → vent + drain 존재 |
| VAL-EQP-007 | 용기 하부 드레인 밸브 필수 | error | PID | vessel.bottom → drain_valve 존재 |
| VAL-EQP-008 | 용기 상부 벤트 밸브 필수 | error | PID | vessel.top → vent_valve 존재 |
| VAL-EQP-009 | 제어밸브 전후 차단밸브 필수 | error | PID | control_valve 양쪽 → block_valve |
| VAL-EQP-010 | 제어밸브 바이패스 라인 필수 | warning | PID | control_valve → bypass_line 존재 |
| VAL-EQP-011 | 스트레이너/필터 전후 차단밸브 | warning | PID | strainer 양쪽 → block_valve |
| VAL-EQP-012 | 플로우 오리피스 전후 직관부 | info | PID | flow_orifice → straight_pipe 존재 |
| VAL-EQP-013 | 스팀트랩 후단 체크밸브 | warning | PID | steam_trap.downstream → check_valve |
| VAL-EQP-014 | 탱크 오버플로우 라인 필수 | error | PID | atmospheric_tank → overflow_line 존재 |
| VAL-EQP-015 | 회전기기 윤활 시스템 표시 | warning | PID | rotating_equipment → lube_system 존재 |

> reference: 설계 관행 + API/ASME 기반, layer: L2

### 3.5 Validate — 계장/제어루프 규칙 (10건)

| code | name_ko | severity | scope | condition 요약 |
|---|---|---|---|---|
| VAL-INS-001 | 제어루프 최소 구성: 센서+컨트롤러+최종요소 | error | PID | control_loop → sensor + controller + final_element |
| VAL-INS-002 | 계기 태그 첫 글자는 ISA 측정변수 | error | both | instrument.tag[0] ∈ ISA first_letter |
| VAL-INS-003 | 계기 태그 형식 준수 | error | both | instrument.tag matches `[A-Z]{2,4}-\d{3,4}[A-Z]?` |
| VAL-INS-004 | 안전계장 루프(SIF)에 SIL 등급 표기 | error | PID | SIF_loop → SIL_rating 존재 |
| VAL-INS-005 | 알람 설정값 범위 명시 | warning | PID | alarm_instrument → setpoint 존재 |
| VAL-INS-006 | 전송기(T) 출력 신호 타입 표기 | warning | PID | transmitter → signal_type (4-20mA, HART 등) |
| VAL-INS-007 | 계기 위치 표기 (현장/판넬/DCS) | warning | PID | instrument → location 존재 |
| VAL-INS-008 | 동일 루프 내 태그 번호 통일 | error | PID | same_loop instruments → same loop_number |
| VAL-INS-009 | PFD에서 주요 제어루프만 표시 | warning | PFD | PFD에 minor_instrument가 있으면 경고 |
| VAL-INS-010 | 인터락(shutdown) 기능은 별도 표기 | warning | PID | interlock_function → distinct_symbol |

> reference: ISA-5.1 + IEC 61511, layer: L1~L2

### 3.6 Validate — 배관/라인 규칙 (10건)

| code | name_ko | severity | scope | condition 요약 |
|---|---|---|---|---|
| VAL-PIP-001 | 라인넘버 형식 준수 | error | PID | line_number matches `\d+"-[A-Z]{2,4}-\d{3,4}-[A-Z0-9]+` |
| VAL-PIP-002 | 모든 배관에 라인넘버 존재 | error | PID | every edge → line_number ≠ null |
| VAL-PIP-003 | 배관 사이즈 명시 | error | PID | every edge → size ≠ null |
| VAL-PIP-004 | 배관 스펙(Pipe Class) 명시 | error | PID | every edge → spec ≠ null |
| VAL-PIP-005 | PFD에서는 라인넘버 생략 가능 | info | PFD | PFD edge에 line_number 없어도 OK |
| VAL-PIP-006 | 유틸리티 라인 구분 표기 | warning | PID | utility_line → line_style ≠ process_line |
| VAL-PIP-007 | 보온/보냉 타입 표기 | warning | PID | insulated_line → insulation_type 존재 |
| VAL-PIP-008 | 배관 흐름 방향 화살표 | warning | PID | edge → flow_direction 존재 |
| VAL-PIP-009 | 데드엔드(막힌 라인) 경고 | warning | PID | node with only inlet OR only outlet |
| VAL-PIP-010 | 배관 연결 일관성 (사이즈 불일치) | warning | PID | connected edges → size 일치 또는 reducer 존재 |

> reference: PIP PIC001 + 설계 관행, layer: L1~L2

### 3.7 Validate — 도면 완결성 규칙 (8건)

| code | name_ko | severity | scope | condition 요약 |
|---|---|---|---|---|
| VAL-CMP-001 | 모든 장비에 태그 번호 존재 | error | both | every equipment → tag ≠ null |
| VAL-CMP-002 | 모든 장비에 장비명 존재 | error | both | every equipment → name ≠ null |
| VAL-CMP-003 | 장비 태그 중복 금지 | error | both | equipment.tag is unique |
| VAL-CMP-004 | 라인넘버 중복 금지 (동일 도면) | error | PID | edge.line_number is unique per diagram |
| VAL-CMP-005 | 미연결 노드(고아) 경고 | warning | both | node with zero edges → warning |
| VAL-CMP-006 | 배터리 리밋 경계 표시 | warning | both | diagram has battery_limit markers |
| VAL-CMP-007 | 타이틀 블록 필수 항목 | warning | both | title_block has name, number, revision, date |
| VAL-CMP-008 | 도면 내 범례(Legend) 존재 | info | PID | diagram has legend section |

> reference: ISO 10628 + PIP PIC001, layer: L1

### 3.8 Validate — PFD 전용 규칙 (7건)

| code | name_ko | severity | scope | condition 요약 |
|---|---|---|---|---|
| VAL-PFD-001 | PFD에 드레인/벤트 밸브 표시 금지 | warning | PFD | PFD에 drain/vent valve 없어야 함 |
| VAL-PFD-002 | PFD에 바이패스 라인 표시 금지 | warning | PFD | PFD에 bypass_line 없어야 함 |
| VAL-PFD-003 | PFD 스트림에 온도/압력/유량 필수 | error | PFD | PFD stream → T, P, flow_rate 존재 |
| VAL-PFD-004 | PFD 스트림 넘버 순차 | warning | PFD | stream_number 순서 일관성 |
| VAL-PFD-005 | H&MB 테이블 존재 | error | PFD | diagram has hmb_table |
| VAL-PFD-006 | 주요 제어밸브만 표시 | warning | PFD | PFD에 minor_valve 없어야 함 |
| VAL-PFD-007 | 주요 장비 설계조건 표기 | warning | PFD | major_equipment → design_T, design_P |

> reference: ISO 10628-1 + PIP PIE001, layer: L1

### 3.9 Generate — 자동 배치 규칙 (10건)

| code | name_ko | scope | trigger | action 요약 |
|---|---|---|---|---|
| GEN-EQP-001 | 펌프 배치 시 체크밸브 자동 추가 | PID | pump placed | discharge에 check_valve 추가 |
| GEN-EQP-002 | 펌프 배치 시 차단밸브 자동 추가 | PID | pump placed | suction + discharge에 block_valve 추가 |
| GEN-EQP-003 | 압력용기 배치 시 PSV 자동 추가 | PID | pressure_vessel placed | PSV + 입구 차단밸브(CSO) 추가 |
| GEN-EQP-004 | 용기 배치 시 벤트/드레인 자동 추가 | PID | vessel placed | top에 vent, bottom에 drain 추가 |
| GEN-EQP-005 | 제어밸브 배치 시 차단밸브+바이패스 | PID | control_valve placed | 전후 block_valve + bypass 추가 |
| GEN-TAG-001 | 장비 태그 자동 넘버링 | both | equipment placed | 분류코드 + 영역번호 + 순번 |
| GEN-TAG-002 | 라인넘버 자동 생성 | PID | edge created | 사이즈"-유체코드-순번-스펙 |
| GEN-TAG-003 | 계기 태그 자동 넘버링 | both | instrument placed | ISA코드 + 루프번호 |
| GEN-SYM-001 | 심볼 자동 선택 | both | node type 결정 시 | subtype → SVG 심볼 매핑 |
| GEN-LIN-001 | 선종 자동 스타일 | both | edge type 결정 시 | process/utility/signal → 선 스타일 |

> layer: L2~L3

---

## 4. 규칙 요약 통계

| 구분 | 건수 |
|---|---|
| Lookup — ISA 문자코드 | 26 |
| Lookup — ISA 기능문자 | 12 |
| Lookup — PIP 장비분류 | 12 |
| Validate — 필수 요소 | 15 |
| Validate — 계장/제어루프 | 10 |
| Validate — 배관/라인 | 10 |
| Validate — 도면 완결성 | 8 |
| Validate — PFD 전용 | 7 |
| Generate — 자동 배치 | 10 |
| **합계** | **110** |

### 규칙 커버리지

```
현재 110건 / 목표 ~550건 = 약 20%

커버된 영역:
  ✅ ISA 문자코드 체계
  ✅ PIP 장비분류 체계
  ✅ 핵심 설계 관행 (펌프, 밸브, PSV)
  ✅ 태그/라인넘버 형식
  ✅ 제어루프 기본 구성
  ✅ PFD vs P&ID 구분 규칙
  ✅ 도면 완결성

아직 미커버:
  ❌ ISA 심볼 형태 규칙 (~100건)
  ❌ ISO 10628 장비/밸브 심볼 매핑 (~80건)
  ❌ 상세 배관 규칙 (Pipe Class, 재질) (~50건)
  ❌ 안전계장 상세 (SIL, LOPA) (~30건)
  ❌ 유틸리티 계통 규칙 (~40건)
  ❌ 공정 특화 규칙 (PLA, Compound) (~50건)
  ❌ 회사/프로젝트 규칙 (~90건)
```

---

## 5. 다음 단계

1. **DDL 생성** — 위 스키마를 SQLite DDL로 변환
2. **시드 JSON 생성** — 110건 규칙을 db/seeds/ JSON 파일로 변환
3. **시드 로더 구현** — seed_loader.py로 DB 초기화
4. **CRUD API** — FastAPI 라우터 구현
5. **검증 API** — validator.py에 그래프 패턴 매칭 구현
