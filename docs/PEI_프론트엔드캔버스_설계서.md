# PEI 프론트엔드 캔버스 설계서

---

## 1. 화면 레이아웃

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar                                                    │
│  File | Edit | View | Insert | Validate | Generate | Export  │
├────────┬──────────────────────────────────┬─────────────────┤
│        │                                  │                 │
│ Symbol │        P&ID Canvas               │   Property      │
│ Palette│        (ReactFlow)               │   Panel         │
│        │                                  │                 │
│ ┌────┐ │                                  │  ┌───────────┐  │
│ │펌프│ │    ┌───┐    ┌───┐    ┌───┐       │  │Tag: P-101 │  │
│ ├────┤ │    │R  │───▶│CV │───▶│E  │       │  │Type: Pump │  │
│ │밸브│ │    │101│    │101│    │101│       │  │Design P:  │  │
│ ├────┤ │    └───┘    └───┘    └───┘       │  │Design T:  │  │
│ │계기│ │      │                            │  │Material:  │  │
│ ├────┤ │    ┌───┐                          │  └───────────┘  │
│ │용기│ │    │TIC│                          │                 │
│ ├────┤ │    │101│                          │  ┌───────────┐  │
│ │기타│ │    └───┘                          │  │ Nozzles   │  │
│ └────┘ │                                  │  │ N1: Feed  │  │
│        │                                  │  │ N2: Prod  │  │
│        │                                  │  └───────────┘  │
│  200px │              flex                │     300px       │
├────────┴──────────────────────────────────┴─────────────────┤
│  Problems Panel (검증 결과)                                   │
│  ❌ P-101: 토출측 체크밸브 없음  ⚠️ E-101: 벤트밸브 없음      │
│                                                    200px    │
├─────────────────────────────────────────────────────────────┤
│  Status Bar: PID-001 v3 | 규칙셋: pei-default v1 | 노드:12  │
└─────────────────────────────────────────────────────────────┘
```

### 패널 크기/토글

| 패널 | 기본 너비/높이 | 토글 | 단축키 |
|---|---|---|---|
| Symbol Palette | 200px | 접기/펼치기 | `Ctrl+1` |
| Property Panel | 300px | 접기/펼치기 | `Ctrl+2` |
| Problems Panel | 200px (높이) | 접기/펼치기 | `Ctrl+3` |
| Minimap | 150×100px (우하단 오버레이) | 토글 | `Ctrl+M` |

---

## 2. 컴포넌트 구조

```
frontend/src/
├── components/
│   ├── canvas/
│   │   ├── PidCanvas.tsx            # ReactFlow 메인 캔버스
│   │   ├── PidMinimap.tsx           # 미니맵
│   │   ├── nodes/                   # 커스텀 노드 컴포넌트
│   │   │   ├── EquipmentNode.tsx    #   장비 노드 (SVG 심볼 렌더링)
│   │   │   ├── ValveNode.tsx        #   밸브 노드
│   │   │   ├── InstrumentNode.tsx   #   계기 노드
│   │   │   └── NozzleNode.tsx       #   노즐 (포트)
│   │   ├── edges/
│   │   │   ├── ProcessEdge.tsx      #   공정 배관 (실선)
│   │   │   ├── UtilityEdge.tsx      #   유틸리티 배관 (파선)
│   │   │   └── SignalEdge.tsx       #   신호선 (점선)
│   │   └── overlays/
│   │       ├── ValidationOverlay.tsx #  검증 위반 표시 (빨간 테두리)
│   │       └── TagLabel.tsx          #  태그/라인넘버 라벨
│   │
│   ├── panels/
│   │   ├── SymbolPalette.tsx        # 좌측 심볼 팔레트
│   │   ├── PropertyPanel.tsx        # 우측 속성 편집
│   │   ├── ProblemsPanel.tsx        # 하단 검증 결과
│   │   ├── ConceptConfirm.tsx       # 컨셉 확인 화면 (BFD + 조건표)
│   │   └── ExportDialog.tsx         # 내보내기 다이얼로그
│   │
│   └── common/
│       ├── MenuBar.tsx              # 상단 메뉴
│       ├── StatusBar.tsx            # 하단 상태바
│       ├── CommandPalette.tsx       # Ctrl+Shift+P 커맨드 팔레트
│       └── Toolbar.tsx              # 도구 모음
│
├── stores/
│   ├── canvas-store.ts              # 노드/엣지 상태 (Zustand)
│   ├── project-store.ts             # 프로젝트/도면 상태
│   ├── validation-store.ts          # 검증 결과 상태
│   └── ui-store.ts                  # 패널 토글, 선택 상태
│
├── services/
│   ├── api-client.ts                # axios 인스턴스 + 인터셉터
│   ├── diagram-api.ts               # 도면 CRUD API 호출
│   ├── rule-api.ts                  # 규칙/검증 API 호출
│   ├── generate-api.ts              # 생성 API 호출
│   └── export-api.ts                # 내보내기 API 호출
│
├── converters/
│   ├── to-canonical.ts              # ReactFlow → Canonical
│   └── to-reactflow.ts             # Canonical → ReactFlow
│
├── symbols/
│   ├── equipment/
│   │   ├── pump.svg
│   │   ├── vessel.svg
│   │   ├── heat-exchanger.svg
│   │   ├── reactor.svg
│   │   ├── column.svg
│   │   ├── tank.svg
│   │   ├── compressor.svg
│   │   └── ...
│   ├── valves/
│   │   ├── gate-valve.svg
│   │   ├── globe-valve.svg
│   │   ├── check-valve.svg
│   │   ├── control-valve.svg
│   │   ├── ball-valve.svg
│   │   ├── butterfly-valve.svg
│   │   ├── safety-valve.svg
│   │   └── ...
│   ├── instruments/
│   │   ├── field-mounted.svg        # 원형 (현장)
│   │   ├── panel-mounted.svg        # 원형 + 가로선 (판넬)
│   │   ├── dcs-shared.svg           # 원형 + 사각 (DCS)
│   │   └── plc-mounted.svg          # 사각 (PLC)
│   ├── piping/
│   │   ├── reducer.svg
│   │   ├── tee.svg
│   │   └── blind-flange.svg
│   └── index.ts                     # 심볼 레지스트리
│
├── reference/
│   ├── isa-codes.ts                 # ISA 문자코드 캐시
│   ├── equipment-classes.ts         # 장비분류 캐시
│   └── line-styles.ts               # 선종 스타일 캐시
│
└── types/
    ├── canonical.ts                 # Canonical Diagram 타입
    └── ui.ts                        # ReactFlow UI 타입
```

---

## 3. 캔버스 핵심 기능

### 3.1 노드 배치 (드래그 & 드롭)

```
사용자 동작:
  Symbol Palette에서 "펌프" 드래그 → 캔버스에 드롭

처리 흐름:
  1. onDrop 이벤트 → 마우스 좌표를 캔버스 좌표로 변환
  2. 새 노드 생성 (id, type, subtype, position)
  3. 태그 자동 넘버링 (GEN-TAG-001 규칙 적용)
     → 기존 펌프: P-101 → 새 펌프: P-102
  4. canvas-store에 노드 추가
  5. (옵션) generate/template API 호출
     → 체크밸브, 차단밸브 자동 추가 제안
  6. 자동 추가 노드를 점선으로 표시 (사용자 확인 대기)
  7. 사용자 "적용" → 실선으로 전환
```

### 3.2 라인 연결

```
사용자 동작:
  노드의 포트(노즐)에서 드래그 → 다른 노드의 포트에 드롭

처리 흐름:
  1. onConnect 이벤트 → source/target 노드+포트 확인
  2. 새 엣지 생성
  3. 라인넘버 자동 생성 (GEN-TAG-002 규칙)
     → 사이즈"-유체코드-순번-스펙
  4. canvas-store에 엣지 추가
  5. 디바운스 500ms 후 validate/quick API 호출
  6. 위반 있으면 Problems Panel에 표시 + 노드 빨간 테두리
```

### 3.3 실시간 검증 피드백

```
트리거:
  노드 배치, 라인 연결, 속성 변경 후 500ms 디바운스

동작:
  ┌─ 변경된 노드/엣지 감지
  │
  ▼ validate/quick API 호출 (변경된 노드만)
  │
  ├─ 위반 없음 → 녹색 체크 표시 (잠시 후 사라짐)
  │
  └─ 위반 있음
     ├─ error: 빨간 테두리 + Problems Panel에 ❌ 표시
     ├─ warning: 주황 테두리 + Problems Panel에 ⚠️ 표시
     └─ info: 파란 점 + Problems Panel에 ℹ️ 표시

Problems Panel 항목 클릭 시:
  → 해당 노드로 캔버스 이동 + 줌 + 하이라이트
  → auto_repairable이면 "자동 수정" 버튼 표시
```

### 3.4 전체 검증 실행

```
트리거:
  메뉴 > Validate > Run All (Ctrl+Shift+V)

동작:
  1. canonical로 변환 (to-canonical.ts)
  2. POST /validate API 호출
  3. 결과를 validation-store에 저장
  4. Problems Panel에 전체 위반 목록 표시
  5. 캔버스에 모든 위반 노드 하이라이트
  6. Status Bar에 "❌ 4 errors, ⚠️ 2 warnings" 표시
```

---

## 4. Zustand 스토어 설계

### 4.1 canvas-store.ts

```typescript
interface CanvasState {
  // 노드/엣지 (ReactFlow 형식)
  nodes: Node[];
  edges: Edge[];

  // 선택 상태
  selectedNodeIds: string[];
  selectedEdgeIds: string[];

  // 액션
  addNode: (node: CanonicalNode, position: XYPosition) => void;
  removeNode: (id: string) => void;
  updateNodeData: (id: string, data: Partial<NodeData>) => void;
  addEdge: (connection: Connection) => void;
  removeEdge: (id: string) => void;

  // ReactFlow 이벤트 핸들러
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;

  // 변환
  toCanonical: () => DiagramCanonical;
  loadFromCanonical: (canonical: DiagramCanonical) => void;

  // 이력 (undo/redo)
  history: CanvasSnapshot[];
  historyIndex: number;
  undo: () => void;
  redo: () => void;
  pushSnapshot: () => void;
}
```

### 4.2 validation-store.ts

```typescript
interface ValidationState {
  // 최근 전체 검증 결과
  lastRun: ValidationReport | null;
  isValidating: boolean;

  // 실시간 위반 (노드별)
  nodeViolations: Map<string, Violation[]>;
  edgeViolations: Map<string, Violation[]>;

  // 액션
  runFullValidation: (diagramId: string, rulesetId: string) => Promise<void>;
  runQuickValidation: (targetId: string) => Promise<void>;
  clearViolations: () => void;

  // 조회
  getViolationsForNode: (nodeId: string) => Violation[];
  getErrorCount: () => number;
  getWarningCount: () => number;
}
```

### 4.3 project-store.ts

```typescript
interface ProjectState {
  // 현재 프로젝트/도면
  currentProject: Project | null;
  currentDiagram: Diagram | null;
  activeRuleset: Ruleset | null;

  // 도면 상태
  isDirty: boolean;           // 미저장 변경 존재
  lastSavedVersion: number;

  // 액션
  loadProject: (id: string) => Promise<void>;
  loadDiagram: (id: string) => Promise<void>;
  saveDiagram: () => Promise<void>;
  createNewDiagram: (type: DiagramType) => Promise<void>;

  // 자동 저장
  autoSaveInterval: number;   // ms (기본 30000)
  enableAutoSave: boolean;
}
```

### 4.4 ui-store.ts

```typescript
interface UIState {
  // 패널 가시성
  showSymbolPalette: boolean;
  showPropertyPanel: boolean;
  showProblemsPanel: boolean;
  showMinimap: boolean;
  showCommandPalette: boolean;

  // 토글
  toggleSymbolPalette: () => void;
  togglePropertyPanel: () => void;
  toggleProblemsPanel: () => void;
  toggleMinimap: () => void;
  toggleCommandPalette: () => void;

  // 캔버스 뷰
  zoom: number;
  panPosition: { x: number; y: number };
}
```

---

## 5. 커스텀 노드 렌더링

### 5.1 EquipmentNode 구조

```typescript
// components/canvas/nodes/EquipmentNode.tsx

interface EquipmentNodeData {
  tag: string;                    // P-101
  name: string;                   // Centrifugal Pump
  subtype: string;                // pump
  symbolId: string;               // pump.svg 참조
  properties: Record<string, any>;
  nozzles: Nozzle[];
  validationStatus: 'valid' | 'error' | 'warning' | null;
}

// 렌더링 구조:
// ┌──────────────────────────┐
// │  [SVG 심볼]              │ ← 장비 심볼 (symbols/ 폴더 참조)
// │                          │
// │  ○ N1(inlet)  N2(outlet)○│ ← 노즐 = ReactFlow Handle (포트)
// │                          │
// │  P-101                   │ ← 태그 라벨
// │  Centrifugal Pump        │ ← 장비명 (줌 레벨에 따라 표시/숨김)
// └──────────────────────────┘
//
// validationStatus에 따라 테두리 색상:
//   valid   → 없음 (기본)
//   error   → 빨간 테두리 + 빨간 점
//   warning → 주황 테두리 + 주황 점
```

### 5.2 InstrumentNode 구조

```
ISA 심볼 표현:

현장 계기:           판넬 계기:          DCS 공유:
  ┌───┐               ┌───┐              ┌───┐
  │TIC│               │TIC│              │TIC│
  │101│           ────│101│          ╔═══│101│
  └───┘               └───┘              └───┘
  (원형)              (원형+가로선)       (원형+사각)

렌더링:
  1. location 속성에 따라 심볼 형태 결정
  2. 태그 텍스트를 심볼 내부에 표시
  3. 첫 줄: 기능문자 (TIC)
  4. 둘 줄: 루프번호 (101)
```

### 5.3 엣지(배관) 렌더링

```
선종별 스타일:

공정 배관:     ────────────      실선, 검정, 굵기 2px
유틸리티:      ── ── ── ──      파선, 검정, 굵기 1.5px
신호선(전기):  ─ ─ ─ ─ ─ ─      점선, 검정, 굵기 1px
신호선(공압):  ─ ─×─ ─×─ ─      점선 + X 마크
질소/불활성:   ────N2────        실선 + 유체 라벨
스팀:          ────STM───        실선 + 유체 라벨

라벨 표시:
  라인넘버: 6"-PLA-001-A1A
  위치: 엣지 중간, 배경 흰색 박스
  줌 80% 이하에서 숨김
```

---

## 6. 단축키 맵

| 단축키 | 동작 |
|---|---|
| `Ctrl+S` | 저장 |
| `Ctrl+Z` | 실행 취소 (Undo) |
| `Ctrl+Shift+Z` | 다시 실행 (Redo) |
| `Ctrl+Shift+V` | 전체 검증 실행 |
| `Ctrl+Shift+P` | 커맨드 팔레트 열기 |
| `Ctrl+1` | 심볼 팔레트 토글 |
| `Ctrl+2` | 속성 패널 토글 |
| `Ctrl+3` | 문제 패널 토글 |
| `Ctrl+M` | 미니맵 토글 |
| `Delete` | 선택 노드/엣지 삭제 |
| `Ctrl+A` | 전체 선택 |
| `Ctrl+C/V` | 복사/붙여넣기 |
| `Ctrl+D` | 선택 항목 복제 |
| `Ctrl+G` | 그룹 생성 |
| `Ctrl+F` | 태그/장비 검색 |
| `Space + 드래그` | 캔버스 팬 |
| `Ctrl + 스크롤` | 줌 인/아웃 |
| `Ctrl+0` | 줌 맞추기 (Fit View) |

---

## 7. 심볼 팔레트 구성

```
Symbol Palette
├── 📁 장비 (Equipment)
│   ├── 펌프 (Pump)
│   │   ├── 원심펌프
│   │   ├── 왕복동펌프
│   │   └── 기어펌프
│   ├── 용기 (Vessel)
│   │   ├── 수직 드럼
│   │   ├── 수평 드럼
│   │   └── 분리기
│   ├── 열교환기 (Heat Exchanger)
│   │   ├── Shell & Tube
│   │   ├── Plate
│   │   └── Air Cooler
│   ├── 반응기 (Reactor)
│   │   ├── CSTR
│   │   └── Plug Flow
│   ├── 탑/칼럼 (Column)
│   ├── 탱크 (Tank)
│   ├── 압축기 (Compressor)
│   └── 기타 (Misc)
│       ├── 믹서
│       ├── 필터
│       └── 건조기
│
├── 📁 밸브 (Valve)
│   ├── 게이트밸브 (Gate)
│   ├── 글로브밸브 (Globe)
│   ├── 볼밸브 (Ball)
│   ├── 버터플라이밸브 (Butterfly)
│   ├── 체크밸브 (Check)
│   ├── 제어밸브 (Control)
│   ├── 안전밸브 (Safety/PSV)
│   └── 3-way 밸브
│
├── 📁 계기 (Instrument)
│   ├── 유량 (F~)
│   ├── 레벨 (L~)
│   ├── 압력 (P~)
│   ├── 온도 (T~)
│   └── 분석 (A~)
│
├── 📁 배관 부속 (Fittings)
│   ├── 리듀서
│   ├── 티 (Tee)
│   └── 블라인드 플랜지
│
└── 🔍 검색 (Search)
    └── [태그 또는 이름으로 검색]
```

계기를 팔레트에서 선택하면, ISA 문자코드 기반으로 측정변수(첫글자)와 기능문자(후속글자)를 조합하는 UI를 제공한다.

```
계기 추가 다이얼로그:
┌──────────────────────────────┐
│ 측정변수:  [T ▼] Temperature │
│ 기능:      [I ▼] Indicate   │
│            [C ✓] Control    │
│ 결과 태그: TIC-___          │
│ 루프번호:  [101]             │
│ 위치:      [현장 ▼]          │
│                              │
│     [취소]  [추가]           │
└──────────────────────────────┘
```

---

## 8. 컨셉 확인 화면 (ConceptConfirm)

자연어 입력 → AI 해석 → 사용자 확인 단계의 UI.

```
┌─────────────────────────────────────────────────────────────┐
│  컨셉 확인                                          [닫기]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  공정 개요 (BFD)                                            │
│  ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐         │
│  │ 원료  │───▶│ 반응  │───▶│ 분리  │───▶│ 성형  │         │
│  │ 저장  │    │ (ROP) │    │(탈휘) │    │(펠릿) │         │
│  └───────┘    └───────┘    └───────┘    └───────┘         │
│                   ▲                                        │
│                   │ N₂                                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  주요 설계 조건                                              │
│  ┌──────────────────┬──────────────┬───────┐               │
│  │ 항목             │ 값           │ 상태  │               │
│  ├──────────────────┼──────────────┼───────┤               │
│  │ 생산용량         │ 30,000 TPA   │ ✅    │               │
│  │ 원료             │ L-Lactide    │ ✅    │               │
│  │ 반응 방식        │ 개환중합     │ ✅    │               │
│  │ 질소 블랭킷      │ 필수         │ ✅    │               │
│  │ 운전 시간        │ [8,000 hr/yr]│ 💡    │ ← 기본값 제안  │
│  │ 설계 온도        │ [220 °C]     │ 💡    │               │
│  │ 설계 압력        │ [___]        │ ⚠️    │ ← 미입력       │
│  └──────────────────┴──────────────┴───────┘               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  예상 주요 장비                                              │
│  ┌────┬───────────────────┬──────┬──────────────┐          │
│  │ #  │ 장비              │ 분류 │ 근거         │          │
│  ├────┼───────────────────┼──────┼──────────────┤          │
│  │ 1  │ 원료 저장 탱크    │ TK   │ 원료 저장    │          │
│  │ 2  │ 중합 반응기       │ R    │ 개환중합     │          │
│  │ 3  │ 탈휘 장치         │ V    │ 잔류 모노머  │          │
│  │ 4  │ 펠릿타이저        │ U    │ 제품 성형    │          │
│  │ 5  │ N₂ 공급 시스템    │ -    │ 질소 블랭킷  │          │
│  └────┴───────────────────┴──────┴──────────────┘          │
│                                                             │
│  ⚠️ 미입력 항목을 채워주세요                                  │
│                                                             │
│           [✏️ 수정하기]  [✅ 이대로 진행]                    │
└─────────────────────────────────────────────────────────────┘
```

**상태 아이콘:**
- ✅ 사용자 입력 확인됨
- 💡 기본값 제안 (규격 DB에서 가져옴, 클릭하면 수락/수정)
- ⚠️ 미입력 (필수 항목이면 진행 불가)

---

## 9. 데이터 흐름

### 9.1 도면 로드

```
사용자: 도면 열기
    │
    ▼
GET /diagrams/{id}
    │ canonical_json 수신
    ▼
to-reactflow.ts
    │ Canonical → ReactFlow 노드/엣지 변환
    ▼
canvas-store.ts
    │ nodes, edges 상태 업데이트
    ▼
PidCanvas.tsx
    │ ReactFlow 렌더링
    ▼
화면에 P&ID 표시
```

### 9.2 도면 저장

```
사용자: Ctrl+S
    │
    ▼
canvas-store.toCanonical()
    │ ReactFlow → Canonical 변환
    ▼
PUT /diagrams/{id}
    │ canonical_json 전송
    │ version 자동 +1
    ▼
project-store.ts
    │ isDirty = false, lastSavedVersion 업데이트
    ▼
Status Bar: "저장 완료 (v4)"
```

### 9.3 검증 → 자동 수정

```
사용자: 전체 검증 실행 (Ctrl+Shift+V)
    │
    ▼
POST /validate
    │ violations 수신
    ▼
validation-store.ts
    │ 위반 목록 저장
    ▼
PidCanvas: 위반 노드 하이라이트
ProblemsPanel: 위반 목록 표시
    │
    │ 사용자: "자동 수정" 클릭
    ▼
POST /generate/auto-repair
    │ 수정된 canonical_json 수신
    ▼
to-reactflow.ts
    │ 변환
    ▼
canvas-store.ts
    │ 추가된 노드/엣지를 점선으로 표시
    ▼
사용자: "적용" → 실선 전환 + 저장
```

---

## 10. MVP 구현 우선순위

| 순서 | 구현 항목 | 완성 시 가능한 것 |
|---|---|---|
| 1 | PidCanvas + EquipmentNode + 기본 드래그&드롭 | 빈 캔버스에 장비 배치 |
| 2 | 엣지 연결 + ProcessEdge | 장비 간 배관 라인 그리기 |
| 3 | PropertyPanel + 태그/속성 편집 | 장비 스펙 입력 |
| 4 | SymbolPalette (장비, 밸브 기본) | 심볼 팔레트에서 드래그 |
| 5 | to-canonical / to-reactflow 변환기 | 백엔드 연동 준비 완료 |
| 6 | 저장/로드 (diagram API 연동) | 작업 저장 가능 |
| 7 | ProblemsPanel + validate API 연동 | 실시간 검증 피드백 |
| 8 | InstrumentNode + ISA 태그 조합 UI | 계기 추가 가능 |
| 9 | ValveNode + 밸브 심볼 | 밸브 배치 가능 |
| 10 | generate/template 연동 | 자동 배치 (체크밸브 등) |

1~7번이 완료되면 **"P&ID를 그리고, 저장하고, 검증받는"** 기본 루프가 동작한다.
