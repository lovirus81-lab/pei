# PEI 예시 P&ID 시나리오 — 30,000 TPA PLA 펠릿 플랜트

---

## 1. 시나리오 개요

| 항목 | 값 |
|---|---|
| 프로젝트명 | 30K PLA Pellet Plant |
| 도면번호 | PID-100-001 |
| 도면 범위 | Area 100 — 중합 반응 섹션 |
| 제품 | PLA (Poly Lactic Acid) 펠릿 |
| 용량 | 30,000 TPA (톤/년) |
| 원료 | L-Lactide |
| 반응 방식 | 개환중합 (Ring-Opening Polymerization) |

이 시나리오는 PEI의 전체 워크플로우를 시연하기 위한 예시이다.

```
사용자 입력 → 컨셉 확인 → P&ID 생성 → 검증 → 자동 수정 → 산출물 추출
```

---

## 2. Step 1 — 사용자 입력

```
"30,000톤/년 PLA 펠릿 플랜트의 중합 반응 섹션 P&ID를 작성해줘.
 L-Lactide 원료를 개환중합으로 반응시킨다.
 반응기는 질소 분위기 필수이고, 촉매를 사용한다.
 반응 온도 180~220°C, 반응 압력 상압~2 barg.
 반응 후 탈휘(devolatilization)로 잔류 모노머를 제거한다."
```

---

## 3. Step 2 — 컨셉 확인

### 3.1 공정 개요 (BFD)

```
   촉매 저장          N₂ 공급
      │                  │
      ▼                  ▼
┌─────────┐    ┌─────────────┐    ┌───────────┐    ┌──────────┐
│  원료   │───▶│   중합      │───▶│   탈휘    │───▶│  다음    │
│  공급   │    │   반응기    │    │   장치    │    │  섹션    │
│ (Lactide)│    │(ROP, N₂)   │    │(Devolatil.)│   │ (펠릿)  │
└─────────┘    └─────────────┘    └───────────┘    └──────────┘
                     │                   │
                     ▼                   ▼
               열매체(HTM)          회수 모노머
               순환 시스템          (재활용)
```

### 3.2 주요 설계 조건

| 항목 | 값 | 상태 | 출처 |
|---|---|---|---|
| 생산용량 | 30,000 TPA | ✅ 입력됨 | 사용자 |
| 원료 | L-Lactide | ✅ 입력됨 | 사용자 |
| 반응 방식 | 개환중합 (ROP) | ✅ 입력됨 | 사용자 |
| 질소 블랭킷 | 필수 | ✅ 입력됨 | 사용자 |
| 촉매 사용 | 예 (Sn(Oct)₂) | ✅ 입력됨 | 사용자 |
| 반응 온도 | 180~220 °C | ✅ 입력됨 | 사용자 |
| 반응 압력 | 0~2 barg | ✅ 입력됨 | 사용자 |
| 설계 온도 | 250 °C | 💡 제안 | 규격 DB (L5: 운전온도 + 마진 30°C) |
| 설계 압력 | 5 barg | 💡 제안 | 규격 DB (L5: 운전압력 × 2.5 또는 +3) |
| 운전 시간 | 8,000 hr/yr | 💡 제안 | 규격 DB (L2: 화학플랜트 표준) |
| 반응기 재질 | SS316L | 💡 제안 | 규격 DB (L5: PLA 공정, 유기산 내식) |
| 열매체 | Therminol 66 | 💡 제안 | 규격 DB (L5: 200°C+ 반응용) |

### 3.3 예상 주요 장비

| # | Tag | 장비 | 분류 | 용도 |
|---|---|---|---|---|
| 1 | TK-101 | Lactide Feed Tank | T (Tank) | 원료 저장 |
| 2 | P-101 A/B | Lactide Feed Pump | J (Liquid) | 원료 이송 |
| 3 | R-101 | Polymerization Reactor | L (Reactor) | 개환중합 반응 |
| 4 | E-101 | Reactor Heater (HTM) | A (Heat Transfer) | 반응 온도 유지 |
| 5 | V-101 | Devolatilizer | R (Vessel) | 잔류 모노머 제거 |
| 6 | E-102 | Devolatilizer Condenser | A (Heat Transfer) | 모노머 증기 응축 |
| 7 | V-102 | Monomer Recovery Drum | R (Vessel) | 회수 모노머 저장 |
| 8 | P-102 A/B | Polymer Transfer Pump | J (Liquid) | 폴리머 이송 |
| 9 | TK-102 | Catalyst Feed Tank | T (Tank) | 촉매 저장 |
| 10 | P-103 | Catalyst Metering Pump | J (Liquid) | 촉매 정량 주입 |

---

## 4. Step 3 — P&ID Canonical JSON (생성 결과)

### 4.1 노드 목록 (39개)

**장비 (10)**

| id | type | subtype | tag | name |
|---|---|---|---|---|
| eq-001 | equipment | tank | TK-101 | Lactide Feed Tank |
| eq-002 | equipment | centrifugal_pump | P-101A | Lactide Feed Pump A |
| eq-003 | equipment | centrifugal_pump | P-101B | Lactide Feed Pump B (Spare) |
| eq-004 | equipment | reactor | R-101 | Polymerization Reactor |
| eq-005 | equipment | heat_exchanger | E-101 | Reactor HTM Heater |
| eq-006 | equipment | vessel | V-101 | Devolatilizer |
| eq-007 | equipment | heat_exchanger | E-102 | Devolatilizer Condenser |
| eq-008 | equipment | vessel | V-102 | Monomer Recovery Drum |
| eq-009 | equipment | tank | TK-102 | Catalyst Feed Tank |
| eq-010 | equipment | metering_pump | P-103 | Catalyst Metering Pump |

**밸브 (18)**

| id | type | subtype | tag | 위치/용도 |
|---|---|---|---|---|
| vv-001 | valve | gate_valve | HV-1001 | TK-101 출구 차단밸브 |
| vv-002 | valve | check_valve | CV-1001 | P-101A 토출 체크밸브 |
| vv-003 | valve | gate_valve | HV-1002 | P-101A 토출 차단밸브 |
| vv-004 | valve | check_valve | CV-1002 | P-101B 토출 체크밸브 |
| vv-005 | valve | gate_valve | HV-1003 | P-101B 토출 차단밸브 |
| vv-006 | valve | control_valve | FV-1001 | Lactide 유량 제어밸브 |
| vv-007 | valve | gate_valve | HV-1004 | FV-1001 상류 차단밸브 |
| vv-008 | valve | gate_valve | HV-1005 | FV-1001 하류 차단밸브 |
| vv-009 | valve | safety_valve | PSV-1001 | R-101 안전밸브 |
| vv-010 | valve | gate_valve | HV-1006 | PSV-1001 입구 차단(CSO) |
| vv-011 | valve | gate_valve | HV-1007 | R-101 하부 드레인 |
| vv-012 | valve | gate_valve | HV-1008 | R-101 상부 벤트 |
| vv-013 | valve | control_valve | TV-1001 | HTM 온도 제어밸브 |
| vv-014 | valve | safety_valve | PSV-1002 | V-101 안전밸브 |
| vv-015 | valve | gate_valve | HV-1009 | PSV-1002 입구 차단(CSO) |
| vv-016 | valve | gate_valve | HV-1010 | V-101 하부 드레인 |
| vv-017 | valve | gate_valve | HV-1011 | V-101 상부 벤트 |
| vv-018 | valve | check_valve | CV-1003 | P-103 토출 체크밸브 |

**계기 (11)**

| id | type | subtype | tag | 기능 | 위치 |
|---|---|---|---|---|---|
| in-001 | instrument | indicator_controller | FIC-1001 | Lactide 유량 지시/제어 | DCS |
| in-002 | instrument | transmitter | FT-1001 | Lactide 유량 전송기 | 현장 |
| in-003 | instrument | indicator_controller | TIC-1001 | 반응기 온도 지시/제어 | DCS |
| in-004 | instrument | transmitter | TT-1001 | 반응기 온도 전송기 | 현장 |
| in-005 | instrument | indicator_controller | PIC-1001 | 반응기 압력 지시/제어 | DCS |
| in-006 | instrument | transmitter | PT-1001 | 반응기 압력 전송기 | 현장 |
| in-007 | instrument | indicator | LI-1001 | TK-101 레벨 지시 | 현장 |
| in-008 | instrument | alarm_high | LAH-1001 | TK-101 고액위 알람 | DCS |
| in-009 | instrument | alarm_low | LAL-1001 | TK-101 저액위 알람 | DCS |
| in-010 | instrument | indicator | TI-1002 | V-101 온도 지시 | 현장 |
| in-011 | instrument | indicator_controller | PIC-1002 | V-101 진공 압력 제어 | DCS |

### 4.2 엣지 목록 (주요 배관 15개)

| id | from | to | line_number | size | spec | fluid |
|---|---|---|---|---|---|---|
| ln-001 | TK-101 | HV-1001 | 3"-LAC-001-A1A | 3" | A1A | L-Lactide |
| ln-002 | HV-1001 | P-101A | 3"-LAC-002-A1A | 3" | A1A | L-Lactide |
| ln-003 | P-101A | CV-1001 | 3"-LAC-003-A1A | 3" | A1A | L-Lactide |
| ln-004 | CV-1001 | HV-1002 | 3"-LAC-004-A1A | 3" | A1A | L-Lactide |
| ln-005 | HV-1002 → HV-1004 | FV-1001 | 3"-LAC-005-A1A | 3" | A1A | L-Lactide |
| ln-006 | FV-1001 | R-101 (N1) | 3"-LAC-006-A1A | 3" | A1A | L-Lactide |
| ln-007 | TK-102 | P-103 | 1"-CAT-001-A1A | 1" | A1A | Catalyst |
| ln-008 | P-103 | R-101 (N2) | 1"-CAT-002-A1A | 1" | A1A | Catalyst |
| ln-009 | E-101 (out) | R-101 (jacket) | 4"-HTM-001-B1A | 4" | B1A | Therminol 66 |
| ln-010 | R-101 (jacket) | E-101 (in) | 4"-HTM-002-B1A | 4" | B1A | Therminol 66 |
| ln-011 | R-101 (N3) | V-101 | 6"-PLA-001-A2A | 6" | A2A | PLA Polymer |
| ln-012 | V-101 (top) | E-102 | 8"-VAP-001-A1A | 8" | A1A | Monomer Vapor |
| ln-013 | E-102 | V-102 | 4"-MON-001-A1A | 4" | A1A | Condensed Monomer |
| ln-014 | V-101 (btm) | P-102A | 6"-PLA-002-A2A | 6" | A2A | PLA Polymer |
| ln-015 | — | R-101 (N4) | 2"-N2-001-C1A | 2" | C1A | Nitrogen |

### 4.3 신호선 (6개)

| id | from | to | signal_type | 설명 |
|---|---|---|---|---|
| sg-001 | FT-1001 | FIC-1001 | 4-20mA | 유량 신호 |
| sg-002 | FIC-1001 | FV-1001 | 4-20mA | 유량 제어 출력 |
| sg-003 | TT-1001 | TIC-1001 | 4-20mA | 온도 신호 |
| sg-004 | TIC-1001 | TV-1001 | 4-20mA | 온도 제어 출력 |
| sg-005 | PT-1001 | PIC-1001 | 4-20mA | 압력 신호 |
| sg-006 | PIC-1002 | (진공펌프 제어) | 4-20mA | 진공 압력 제어 |

### 4.4 제어루프 요약

| Loop | 측정변수 | 센서 | 컨트롤러 | 최종요소 | 동작 |
|---|---|---|---|---|---|
| FIC-1001 | 유량 | FT-1001 | FIC-1001 | FV-1001 | Lactide 유량 제어 |
| TIC-1001 | 온도 | TT-1001 | TIC-1001 | TV-1001 | 반응기 온도 → HTM 유량 |
| PIC-1001 | 압력 | PT-1001 | PIC-1001 | (벤트밸브) | 반응기 압력 제어 |
| PIC-1002 | 압력 | (내장) | PIC-1002 | (진공펌프) | 탈휘 진공도 제어 |

---

## 5. Step 4 — 검증 실행 결과

### 5.1 검증 요약

```
POST /validate
  diagram_id: PID-100-001
  ruleset: pei-default v1

결과:
  총 검사 규칙: 85
  통과: 78
  ❌ error: 4
  ⚠️ warning: 3
  ℹ️ info: 0
```

### 5.2 위반 상세

**❌ Errors**

| # | rule_code | 대상 | 메시지 | auto_repair |
|---|---|---|---|---|
| 1 | VAL-EQP-002 | P-101A | P-101A 흡입측 차단밸브가 없습니다. | ✅ |
| 2 | VAL-EQP-002 | P-101B | P-101B 흡입/토출측 차단밸브가 없습니다. | ✅ |
| 3 | VAL-EQP-006 | E-101 | E-101에 벤트/드레인 밸브가 없습니다. | ✅ |
| 4 | VAL-EQP-006 | E-102 | E-102에 벤트/드레인 밸브가 없습니다. | ✅ |

**⚠️ Warnings**

| # | rule_code | 대상 | 메시지 | auto_repair |
|---|---|---|---|---|
| 5 | VAL-EQP-005 | P-101A | P-101A에 최소유량 바이패스 라인이 없습니다. | ❌ |
| 6 | VAL-EQP-005 | P-101B | P-101B에 최소유량 바이패스 라인이 없습니다. | ❌ |
| 7 | VAL-INS-006 | FT-1001 | FT-1001의 출력 신호 타입이 명시되지 않았습니다. | ❌ |

### 5.3 검증 결과 분석

```
규칙별 통과 현황:

VAL-EQP-001 (체크밸브)     ✅ P-101A, P-101B, P-103 모두 통과
VAL-EQP-002 (차단밸브)     ❌ P-101A 흡입측 누락, P-101B 전부 누락
VAL-EQP-003 (PSV)          ✅ R-101, V-101 모두 통과
VAL-EQP-004 (PSV CSO)      ✅ PSV-1001, PSV-1002 모두 CSO 표기 확인
VAL-EQP-006 (HX 벤트/드레인) ❌ E-101, E-102 누락
VAL-EQP-007 (용기 드레인)    ✅ R-101, V-101, V-102 통과
VAL-EQP-008 (용기 벤트)      ✅ R-101, V-101, V-102 통과
VAL-EQP-009 (제어밸브 차단)  ✅ FV-1001, TV-1001 통과
VAL-INS-001 (루프 구성)      ✅ FIC-1001, TIC-1001, PIC-1001 통과
VAL-INS-002 (태그 첫글자)    ✅ 전체 계기 통과
VAL-INS-003 (태그 형식)      ✅ 전체 계기 통과
VAL-PIP-001 (라인넘버 형식)  ✅ 전체 배관 통과
VAL-PIP-002 (라인넘버 존재)  ✅ 전체 배관 통과
VAL-CMP-001 (장비 태그)      ✅ 전체 장비 통과
VAL-CMP-003 (태그 중복)      ✅ 중복 없음
```

---

## 6. Step 5 — 자동 수정

### 6.1 Auto-Repair 요청

```
POST /generate/auto-repair
  diagram_id: PID-100-001
  run_id: run-001
  repair_targets: [VAL-EQP-002, VAL-EQP-006]
```

### 6.2 수정 결과

| # | 규칙 | 수정 내용 | 추가된 노드 |
|---|---|---|---|
| 1 | VAL-EQP-002 | P-101A 흡입측에 차단밸브 HV-1012 추가 | vv-019 |
| 2 | VAL-EQP-002 | P-101B 흡입측에 차단밸브 HV-1013 추가 | vv-020 |
| 3 | VAL-EQP-002 | P-101B 토출측에 차단밸브 HV-1014 추가 | vv-021 |
| 4 | VAL-EQP-006 | E-101 상부에 벤트밸브 HV-1015 추가 | vv-022 |
| 5 | VAL-EQP-006 | E-101 하부에 드레인밸브 HV-1016 추가 | vv-023 |
| 6 | VAL-EQP-006 | E-102 상부에 벤트밸브 HV-1017 추가 | vv-024 |
| 7 | VAL-EQP-006 | E-102 하부에 드레인밸브 HV-1018 추가 | vv-025 |

### 6.3 수정 후 재검증

```
수정 후 재검증 결과:
  ❌ error: 0
  ⚠️ warning: 3 (최소유량 바이패스, 신호타입 — 수동 조치 필요)
  ℹ️ info: 0

  → 모든 error 해소, warning만 잔존
```

---

## 7. Step 6 — 산출물 추출

### 7.1 Equipment List

| Tag | Name | Type | Design P (barg) | Design T (°C) | Material | Notes |
|---|---|---|---|---|---|---|
| TK-101 | Lactide Feed Tank | Atmospheric Tank | ATM | 80 | SS304 | N₂ blanket |
| P-101A | Lactide Feed Pump A | Centrifugal Pump | 10 | 100 | SS316L | |
| P-101B | Lactide Feed Pump B | Centrifugal Pump | 10 | 100 | SS316L | Spare |
| R-101 | Polymerization Reactor | CSTR | 5 | 250 | SS316L | N₂ blanket, 촉매 |
| E-101 | Reactor HTM Heater | Shell & Tube HX | 10 | 300 | SS316L/CS | HTM side: B1A |
| V-101 | Devolatilizer | Vertical Vessel | FV/5 | 250 | SS316L | 진공 운전 |
| E-102 | Devolatilizer Condenser | Shell & Tube HX | FV/5 | 250 | SS316L/CS | |
| V-102 | Monomer Recovery Drum | Horizontal Vessel | 3 | 100 | SS304 | |
| TK-102 | Catalyst Feed Tank | Day Tank | ATM | 50 | SS316L | |
| P-103 | Catalyst Metering Pump | Diaphragm Pump | 10 | 50 | SS316L | |

### 7.2 Line List (주요 배관)

| Line No. | From | To | Size | Spec | Fluid | Insul. | T (°C) | P (barg) |
|---|---|---|---|---|---|---|---|---|
| 3"-LAC-001-A1A | TK-101 | P-101A | 3" | A1A | L-Lactide | H | 80 | ATM |
| 3"-LAC-006-A1A | FV-1001 | R-101 | 3" | A1A | L-Lactide | H | 80 | 2 |
| 1"-CAT-001-A1A | TK-102 | P-103 | 1" | A1A | Catalyst | - | 25 | ATM |
| 4"-HTM-001-B1A | E-101 | R-101 | 4" | B1A | Therminol 66 | H | 250 | 5 |
| 6"-PLA-001-A2A | R-101 | V-101 | 6" | A2A | PLA Polymer | H | 200 | 2 |
| 8"-VAP-001-A1A | V-101 | E-102 | 8" | A1A | Monomer Vapor | H | 200 | FV |
| 6"-PLA-002-A2A | V-101 | P-102A | 6" | A2A | PLA Polymer | H | 200 | FV |
| 2"-N2-001-C1A | (Header) | R-101 | 2" | C1A | Nitrogen | - | 25 | 6 |

### 7.3 Valve List (일부)

| Tag | Type | Size | Rating | Line No. | Fail Action | Notes |
|---|---|---|---|---|---|---|
| HV-1001 | Gate | 3" | 150# | 3"-LAC-001 | - | TK-101 출구 차단 |
| CV-1001 | Check | 3" | 150# | 3"-LAC-003 | - | P-101A 토출 |
| FV-1001 | Control (Globe) | 3" | 150# | 3"-LAC-005 | FC | Lactide 유량 제어 |
| PSV-1001 | Safety (Spring) | 2"×3" | 150# | - | - | R-101 과압 보호, Set: 5 barg |
| TV-1001 | Control (Globe) | 4" | 150# | 4"-HTM-001 | FC | HTM 온도 제어 |
| PSV-1002 | Safety (Spring) | 2"×3" | 150# | - | - | V-101 과압 보호, Set: 5 barg |

### 7.4 Instrument Index (일부)

| Tag | Service | Range | Output | Location | Loop | P&ID |
|---|---|---|---|---|---|---|
| FT-1001 | Lactide Flow | 0-10 m³/h | 4-20mA HART | Field | FIC-1001 | PID-100-001 |
| FIC-1001 | Lactide Flow | 0-10 m³/h | 4-20mA | DCS | FIC-1001 | PID-100-001 |
| FV-1001 | Lactide Flow | 3" Globe | 4-20mA | Field | FIC-1001 | PID-100-001 |
| TT-1001 | Reactor Temp | 0-300 °C | 4-20mA HART | Field | TIC-1001 | PID-100-001 |
| TIC-1001 | Reactor Temp | 0-300 °C | 4-20mA | DCS | TIC-1001 | PID-100-001 |
| TV-1001 | HTM Temp | 4" Globe | 4-20mA | Field | TIC-1001 | PID-100-001 |
| PT-1001 | Reactor Press | 0-10 barg | 4-20mA HART | Field | PIC-1001 | PID-100-001 |
| LI-1001 | Feed Tank Level | 0-100% | Local | Field | - | PID-100-001 |
| LAH-1001 | Feed Tank Level | H: 90% | DI | DCS | - | PID-100-001 |
| LAL-1001 | Feed Tank Level | L: 10% | DI | DCS | - | PID-100-001 |

---

## 8. Export 번들 내용

```
PEI_PID-100-001_v2_20250219.zip
├── manifest.json
│   {
│     "files": [
│       { "name": "diagram.json", "sha256": "a1b2c3..." },
│       { "name": "diagram.svg", "sha256": "d4e5f6..." },
│       { "name": "validation_report.json", "sha256": "g7h8i9..." },
│       ...
│     ]
│   }
│
├── run_meta.json
│   {
│     "exported_at": "2025-02-19T12:00:00Z",
│     "app_version": "0.1.0",
│     "diagram_version": 2,
│     "total_nodes": 46,
│     "total_edges": 22
│   }
│
├── diagram.json              # Canonical JSON (전체)
├── diagram.svg               # 벡터 P&ID 도면
├── validation_report.json    # 검증 결과 (0 errors, 3 warnings)
├── ruleset_ref.json
│   {
│     "ruleset_name": "pei-default",
│     "ruleset_version": 1,
│     "ruleset_hash": "sha256:xyz789...",
│     "rules_checked": 85,
│     "rules_passed": 82
│   }
│
└── deliverables/
    ├── equipment_list.xlsx    # 장비 10건
    ├── line_list.xlsx         # 배관 15건
    ├── valve_list.xlsx        # 밸브 25건
    └── instrument_index.xlsx  # 계기 11건
```

---

## 9. 시나리오 요약

이 하나의 예시로 PEI의 전체 파이프라인을 시연할 수 있다.

```
[입력]  "30,000톤 PLA 플랜트 중합 섹션"
   │
   ▼
[컨셉 확인]  BFD + 설계조건 10건 + 장비 10건
   │         미입력 항목에 규격 DB 기반 기본값 제안
   ▼
[P&ID 생성]  노드 39개 + 엣지 15개 + 신호선 6개
   │         자동 태그 넘버링, 자동 밸브/계기 배치
   ▼
[검증]  85개 규칙 적용 → 4 errors, 3 warnings
   │    error: 차단밸브 누락, HX 벤트/드레인 누락
   ▼
[자동 수정]  4개 error → 밸브 7개 자동 추가 → 0 errors
   │
   ▼
[산출물]  Equipment List + Line List + Valve List + Instrument Index
   │      재현 가능 번들 (ZIP + manifest + ruleset_ref)
   ▼
[완료]  FEED 검토용 P&ID + 산출물 패키지
```

### 이 시나리오에서 검증된 PEI 기능

| 기능 | 검증 항목 |
|---|---|
| 규격 DB | ISA 태그 검증, PIP 장비분류, 설계관행 규칙 |
| 컨셉 확인 | 기본값 제안 (설계 T/P, 재질, 운전시간) |
| 자동 생성 | 태그 넘버링, 밸브 자동 배치, 제어루프 구성 |
| 검증 엔진 | 필수 요소 검증, 태그 형식, 루프 완결성, 라인넘버 |
| 자동 수정 | 위반 항목 자동 해소 (밸브 추가) |
| 산출물 추출 | 장비/라인/밸브/계기 리스트 자동 생성 |
| 번들 내보내기 | manifest, ruleset_ref, 재현성 보장 |
