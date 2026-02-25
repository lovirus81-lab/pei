"""슬롯 기반 계층적 레이아웃 알고리즘 — 레이아웃 계층"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from app.domain.models.diagram import DiagramCanonical
from app.domain.models.geometry import Position

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
NODE_HEIGHTS: dict[str, int] = {
    "main": 80,
    "valve": 60,
    "instrument": 60
}

Y_BANDS: dict[str, int] = {
    "instrument": 100,
    "valve": 300,
    "main": 550,
}

MAX_SLOT_SEARCH = 1000  # _find_free_slot unbounded 루프 방지


def _get_node_row(subtype: str) -> str:
    if subtype in MAIN_LINE_CLASSES:
        return "main"
    elif subtype in UPPER_LINE_CLASSES:
        return "valve"
    else:
        return "instrument"


def _find_free_slot(occupied: set[Any], preferred_col: int, row: str) -> int:
    """
    특정 row(y_band)에서 선호하는 column을 중심으로 좌우로
    확장하며 비어있는 슬롯을 반환합니다.
    MAX_SLOT_SEARCH 횟수 초과 시 preferred_col + MAX_SLOT_SEARCH 반환.
    """
    if (preferred_col, row) not in occupied:
        return preferred_col

    for offset in range(1, MAX_SLOT_SEARCH):
        if (preferred_col + offset, row) not in occupied:
            return preferred_col + offset
        if (preferred_col - offset, row) not in occupied:
            return preferred_col - offset

    return preferred_col + MAX_SLOT_SEARCH


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

    입력 다이어그램의 노드 position을 in-place로 수정한 뒤 반환한다.
    """
    nodes = {n.id: n for n in diagram.nodes}
    occupied_slots: set[tuple[int, str]] = set()  # (col, row_type)
    node_to_col: dict[str, int] = {}  # n.id -> col

    # 1. 메인라인 탐색: MAIN_LINE_CLASSES 노드만 포함
    out_edges: dict[str, list[str]] = defaultdict(list)
    in_edges: dict[str, list[str]] = defaultdict(list)
    for e in diagram.edges:
        if e.type == "process":
            from_node = nodes.get(e.from_node)
            to_node = nodes.get(e.to_node)
            if (from_node and from_node.subtype in MAIN_LINE_CLASSES
                    and to_node and to_node.subtype in MAIN_LINE_CLASSES):
                out_edges[e.from_node].append(e.to_node)
                in_edges[e.to_node].append(e.from_node)

    # 루트 노드: incoming process 엣지 없는 MAIN_LINE_CLASSES 노드
    main_nodes = [n for n in diagram.nodes if n.subtype in MAIN_LINE_CLASSES]
    roots = [n.id for n in main_nodes if not in_edges[n.id] and out_edges[n.id]]

    if not roots and main_nodes:
        roots = [main_nodes[0].id]

    # BFS로 메인라인 순서 결정
    main_line: list[str] = []
    visited_main: set[str] = set()
    queue: deque[str] = deque(roots)
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

    # 1. 메인라인 노드 위치 할당 (col = 0, 2, 4...) -> 인라인 밸브 공간 확보
    current_col = 0
    for nid in main_line:
        if nid in nodes:
            col = _find_free_slot(occupied_slots, current_col, "main")
            occupied_slots.add((col, "main"))
            node_to_col[nid] = col
            val_x = _col_to_x(col)
            nodes[nid].position = Position(x=val_x, y=_row_to_y("main"))
            current_col = col + 2  # 인라인 밸브를 위해 한 칸 건너뜀

    # 2. 밸브류 노드 할당
    valve_nodes = [n for n in diagram.nodes if n.subtype in UPPER_LINE_CLASSES]
    for n in valve_nodes:
        upstream_main_edges = [
            e for e in diagram.edges
            if e.to_node == n.id
            and nodes.get(e.from_node)
            and nodes.get(e.from_node).subtype in MAIN_LINE_CLASSES
        ]
        downstream_main_edges = [
            e for e in diagram.edges
            if e.from_node == n.id
            and nodes.get(e.to_node)
            and nodes.get(e.to_node).subtype in MAIN_LINE_CLASSES
        ]

        is_inline = bool(upstream_main_edges and downstream_main_edges)

        if is_inline:
            up_id = upstream_main_edges[0].from_node
            down_id = downstream_main_edges[0].to_node
            if up_id in node_to_col and down_id in node_to_col:
                avg_col = (node_to_col[up_id] + node_to_col[down_id]) // 2
                col = avg_col
                if (col, "main") in occupied_slots:
                    col = _find_free_slot(occupied_slots, col, "main")
            else:
                col = _find_free_slot(occupied_slots, current_col, "main")

            occupied_slots.add((col, "main"))
            node_to_col[n.id] = col
            val_x = _col_to_x(col)
            n.position = Position(x=val_x, y=_row_to_y("main"))
        else:
            ref_id = next(
                (e.from_node for e in diagram.edges if e.to_node == n.id and e.from_node in node_to_col),
                next(
                    (e.to_node for e in diagram.edges if e.from_node == n.id and e.to_node in node_to_col),
                    None
                )
            )
            ref_col = node_to_col[ref_id] if ref_id else 0

            col = _find_free_slot(occupied_slots, ref_col, "valve")
            occupied_slots.add((col, "valve"))
            node_to_col[n.id] = col
            val_x = _col_to_x(col)
            n.position = Position(x=val_x, y=_row_to_y("valve"))

    # 3. 계장 노드 할당
    inst_nodes = [n for n in diagram.nodes if n.subtype in INSTRUMENT_CLASSES]
    for n in inst_nodes:
        ref_id = next(
            (e.from_node for e in diagram.edges if e.to_node == n.id and e.from_node in node_to_col),
            next(
                (e.to_node for e in diagram.edges if e.from_node == n.id and e.to_node in node_to_col),
                None
            )
        )
        ref_col = node_to_col[ref_id] if ref_id else 0

        col = _find_free_slot(occupied_slots, ref_col, "instrument")
        occupied_slots.add((col, "instrument"))
        node_to_col[n.id] = col
        val_x = _col_to_x(col)
        n.position = Position(x=val_x, y=_row_to_y("instrument"))

    return diagram
