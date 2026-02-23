from typing import Any
from collections import defaultdict, deque
from app.schemas.canonical import DiagramCanonical, Position

MAIN_LINE_CLASSES = {
    "storage_tank", "centrifugal_pump", "vessel_vertical",
    "vessel_horizontal", "heat_exchanger", "reactor",
    "distillation_column", "filter", "compressor", "dryer", "tank", "vessel"
}

UPPER_LINE_CLASSES = {
    "control_valve", "gate_valve", "check_valve", "relief_valve",
    "butterfly_valve", "ball_valve", "globe_valve", "safety_valve"
}

INSTRUMENT_CLASSES = {
    "temperature_indicator_controller", "level_indicator_controller",
    "flow_indicator_controller", "pressure_indicator_controller",
    "temperature_indicator", "flow_indicator", "pressure_indicator",
    "indicator_controller"
}

def _spread_offset(count: int, step: int) -> int:
    """
    count에 따라 좌우 교대로 오프셋을 반환하는 헬퍼 함수
    0 -> 0
    1 -> +step
    2 -> -step
    3 -> +2*step
    4 -> -2*step
    """
    if count == 0:
        return 0
    multiplier = (count + 1) // 2
    if count % 2 == 1:
        return multiplier * step
    else:
        return -multiplier * step

SLOT_WIDTH = 200
NODE_HEIGHTS = {
    "main": 80,
    "valve": 60,
    "instrument": 60
}

Y_BANDS = {
    "instrument": 100,
    "valve": 300,
    "main": 550,
}

def _get_node_row(subtype: str) -> str:
    if subtype in MAIN_LINE_CLASSES:
        return "main"
    elif subtype in UPPER_LINE_CLASSES:
        return "valve"
    else:
        return "instrument"

def _find_free_slot(occupied: set, preferred_col: int, row: str) -> int:
    """
    특정 row(y_band)에서 선호하는 column을 중심으로 좌우(col+1, col-1, col+2...)로
    확장하며 비어있는 슬롯을 반환합니다.
    """
    if (preferred_col, row) not in occupied:
        return preferred_col

    offset = 1
    while True:
        # Check Right
        if (preferred_col + offset, row) not in occupied:
            return preferred_col + offset
        # Check Left
        if (preferred_col - offset, row) not in occupied:
            return preferred_col - offset
        offset += 1

def _col_to_x(col: int) -> float:
    # 0 -> 80, 1 -> 240, 2 -> 400
    return col * SLOT_WIDTH + (SLOT_WIDTH // 2)

def _row_to_y(row: str) -> float:
    return Y_BANDS[row]

def apply_layout(diagram: DiagramCanonical) -> DiagramCanonical:
    """
    슬롯 분할 기반 계층적 레이아웃 적용
    메인라인: y=550
    상단 분기(bypass, PSV): y=300
    계장(instrument): y=100
    """
    nodes = {n.id: n for n in diagram.nodes}
    occupied_slots = set() # (col, row_type)
    node_to_col = {} # n.id -> col mapping (기준점 추적용)

    # 1. 메인라인 탐색: MAIN_LINE_CLASSES 노드만 포함
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)
    for e in diagram.edges:
        if e.type == "process":
            from_node = nodes.get(e.from_node)
            to_node = nodes.get(e.to_node)
            if from_node and from_node.subtype in MAIN_LINE_CLASSES and to_node and to_node.subtype in MAIN_LINE_CLASSES:
                out_edges[e.from_node].append(e.to_node)
                in_edges[e.to_node].append(e.from_node)

    # 루트 노드: incoming process 엣지 없는 MAIN_LINE_CLASSES 노드
    main_nodes = [n for n in diagram.nodes if n.subtype in MAIN_LINE_CLASSES]
    roots = [n.id for n in main_nodes if not in_edges[n.id] and out_edges[n.id]]

    if not roots and main_nodes:
        # 순환 구조거나 독립된 노드만 있는 경우
        roots = [main_nodes[0].id]

    # BFS로 메인라인 순서 결정
    main_line = []
    visited_main = set()
    queue = deque(roots)
    while queue:
        nid = queue.popleft()
        if nid in visited_main:
            continue
        visited_main.add(nid)
        main_line.append(nid)
        for next_id in out_edges[nid]:
            queue.append(next_id)

    # 누락된 메인라인 노드들을 끝에 추가
    for n in main_nodes:
        if n.id not in visited_main:
            visited_main.add(n.id)
            main_line.append(n.id)

    # 1. 메인라인 노드 위치 할당 (col = 0, 2, 4...) -> 여유 공간을 위해 한 칸씩 건너뜀 (SLOT_WIDTH 160 이므로)
    current_col = 0
    for nid in main_line:
        if nid in nodes:
            # Check for free slot just in case
            col = _find_free_slot(occupied_slots, current_col, "main")
            occupied_slots.add((col, "main"))
            node_to_col[nid] = col
            val_x = _col_to_x(col)
            nodes[nid].position = Position(x=val_x, y=_row_to_y("main"))
            current_col = col + 2 # Leave 1 slot empty for inline valves

    # 2. 밸브류 노드 할당
    valve_nodes = [n for n in diagram.nodes if n.subtype in UPPER_LINE_CLASSES]
    for n in valve_nodes:
        # 상류로 꽂히는 (나에게 들어오는) edge 파악, from_node가 main_line이면 포함
        upstream_main_edges = [
            e for e in diagram.edges 
            if e.to_node == n.id and nodes.get(e.from_node) and nodes.get(e.from_node).subtype in MAIN_LINE_CLASSES
        ]
        
        # 하류로 나가는 (나에게서 나가는) edge 파악, to_node가 main_line이면 포함
        downstream_main_edges = [
            e for e in diagram.edges 
            if e.from_node == n.id and nodes.get(e.to_node) and nodes.get(e.to_node).subtype in MAIN_LINE_CLASSES
        ]
        
        is_inline = bool(upstream_main_edges and downstream_main_edges)
        
        if is_inline:
            # 인라인 밸브: MAIN_Y에 투입 및 X = (upstream_col + downstream_col) / 2
            up_id = upstream_main_edges[0].from_node
            down_id = downstream_main_edges[0].to_node
            if up_id in node_to_col and down_id in node_to_col:
                avg_col = (node_to_col[up_id] + node_to_col[down_id]) // 2
                col = avg_col
                
                # 만약 그 자리를 메인라인 노드(또는 다른 인라인)가 차지하고 있다면 옆으로 밀기
                if (col, "main") in occupied_slots:
                    col = _find_free_slot(occupied_slots, col, "main")
            else:
                col = _find_free_slot(occupied_slots, current_col, "main")
                
            occupied_slots.add((col, "main"))
            node_to_col[n.id] = col
            val_x = _col_to_x(col)
            n.position = Position(x=val_x, y=_row_to_y("main"))
        else:
            # 바이패스 밸브: VALVE_ROW에서 빈 슬롯 탐색
            # 연결된 메인라인 / 인라인 밸브의 col 파악
            ref_col = 0
            ref_id = next(
                (e.from_node for e in diagram.edges if e.to_node == n.id and e.from_node in node_to_col),
                next(
                    (e.to_node for e in diagram.edges if e.from_node == n.id and e.to_node in node_to_col),
                    None
                )
            )
            if ref_id:
                ref_col = node_to_col[ref_id]
                
            col = _find_free_slot(occupied_slots, ref_col, "valve")
            occupied_slots.add((col, "valve"))
            node_to_col[n.id] = col
            val_x = _col_to_x(col)
            n.position = Position(x=val_x, y=_row_to_y("valve"))

    # 3. 계장 노드 할당
    inst_nodes = [n for n in diagram.nodes if n.subtype in INSTRUMENT_CLASSES]
    for n in inst_nodes:
        ref_col = 0
        ref_id = next(
            (e.from_node for e in diagram.edges if e.to_node == n.id and e.from_node in node_to_col),
            next(
                (e.to_node for e in diagram.edges if e.from_node == n.id and e.to_node in node_to_col),
                None
            )
        )
        if ref_id:
            ref_col = node_to_col[ref_id]
            
        col = _find_free_slot(occupied_slots, ref_col, "instrument")
        occupied_slots.add((col, "instrument"))
        node_to_col[n.id] = col
        val_x = _col_to_x(col)
        n.position = Position(x=val_x, y=_row_to_y("instrument"))

    return diagram
