"""자동 수리 서비스 — 순수 도메인 로직, blocking I/O 없음"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.domain.models.diagram import DiagramCanonical, CanonicalNode, CanonicalEdge
from app.domain.models.enums import NodeType, EdgeType
from app.domain.models.geometry import Position
from app.domain.ports.layout_port import ILayoutEngine
from app.domain.services.tag_service import generate_sequential_tag
from app.infrastructure.logging.repair_logger import log_repair_iteration
from app.validation.rule_models import Violation

NODE_Y_OFFSET: dict[str, int] = {
    "relief_valve": -200,
    "safety_valve": -200,
    "control_valve": -200,
    "temperature_indicator_controller": -150,
    "level_indicator_controller": -150,
    "flow_indicator_controller": -150,
    "pressure_indicator_controller": -150,
}
DEFAULT_Y_OFFSET = 0


def _find_free_position(
    nodes: list[CanonicalNode], base_x: float, base_y: float, step: float = 250
) -> tuple[float, float]:
    occupied = {(n.position.x, n.position.y) for n in nodes}
    x = base_x
    while (x, base_y) in occupied:
        x += step
    return x, base_y


def _next_line_number(
    edges: list[CanonicalEdge], fluid: str = "P", size: str = '2"', cls: str = "A1B"
) -> str:
    existing_seqs = []
    for e in edges:
        if getattr(e, 'line_number', None):
            parts = e.line_number.split("-")
            if len(parts) >= 3 and parts[-2].isdigit():
                existing_seqs.append(int(parts[-2]))
    seq = max(existing_seqs, default=100) + 1
    return f'{size}-{fluid}-{seq:03d}-{cls}'


async def auto_repair(
    diagram: DiagramCanonical,
    violations: List[Violation],
    rules: List[Any],
    layout_engine: ILayoutEngine,
) -> Tuple[DiagramCanonical, List[Dict[str, Any]], List[Violation]]:
    """
    위반 목록에 따라 도면을 자동 수정한다.
    - blocking 파일 I/O 없음 (async logging 사용)
    - layout_engine은 외부에서 주입 (의존성 역전)
    - (수정된 다이어그램, 수정 목록, 미수정 위반 목록) 반환
    """
    from app.validation.rule_engine import validate

    repairs_applied: List[Dict[str, Any]] = []
    remaining_violations = violations

    max_iterations = 3
    for iteration in range(max_iterations):
        if not remaining_violations:
            break

        current_repairs: List[Dict[str, Any]] = []
        unfixable: List[Violation] = []

        for v in remaining_violations:
            await log_repair_iteration(
                rule_code=getattr(v, 'rule_code', None),
                node_id=getattr(v, 'node_id', None),
            )

            if v.rule_code == "missing_instrument" and v.node_id:
                node = diagram.node_by_id(v.node_id)
                if node:
                    subtype = "indicator_controller"
                    prefix = "IC"
                    if node.subtype in ("pump", "centrifugal_pump"):
                        prefix = "FIC"
                    elif node.subtype in ("vessel", "tank"):
                        prefix = "LIC"
                    elif node.subtype == "heat_exchanger":
                        prefix = "TIC"

                    inst_tag = generate_sequential_tag(diagram, prefix)
                    y_offset = NODE_Y_OFFSET.get(subtype, DEFAULT_Y_OFFSET)
                    free_x, free_y = _find_free_position(diagram.nodes, node.position.x, node.position.y + y_offset)
                    inst_node = CanonicalNode(
                        type=NodeType.INSTRUMENT,
                        subtype=subtype,
                        tag=inst_tag,
                        location="field",
                        position=Position(x=free_x, y=free_y)
                    )
                    diagram.nodes.append(inst_node)
                    diagram.edges.append(CanonicalEdge(
                        type=EdgeType.SIGNAL_ELECTRICAL,
                        from_node=inst_node.id,
                        to_node=node.id,
                        line_number=f"S-{inst_tag}"
                    ))
                    msg = f"{node.tag}에 {inst_tag} 계기 추가"
                    current_repairs.append({"action": "added_instrument", "node_id": node.id, "new_node_id": inst_node.id, "description": msg})
                    continue

            elif v.rule_code == "missing_valve" and v.edge_id:
                edge = next((e for e in diagram.edges if e.id == v.edge_id), None)
                if edge:
                    src_node = diagram.node_by_id(edge.from_node)
                    tgt_node = diagram.node_by_id(edge.to_node)
                    if src_node and tgt_node:
                        v_tag = generate_sequential_tag(diagram, "XV")
                        vx = src_node.position.x + (tgt_node.position.x - src_node.position.x) / 2
                        vy = src_node.position.y + (tgt_node.position.y - src_node.position.y) / 2
                        free_x, free_y = _find_free_position(diagram.nodes, vx, vy)
                        valve_node = CanonicalNode(
                            type=NodeType.VALVE,
                            subtype="gate_valve",
                            tag=v_tag,
                            position=Position(x=free_x, y=free_y)
                        )
                        diagram.nodes.append(valve_node)
                        edge2 = CanonicalEdge(
                            type=edge.type,
                            from_node=valve_node.id,
                            to_node=edge.to_node,
                            line_number=_next_line_number(diagram.edges)
                        )
                        edge.to_node = valve_node.id
                        diagram.edges.append(edge2)
                        msg = f"{edge.line_number or '라인'}에 {v_tag} 밸브 삽입"
                        current_repairs.append({"action": "added_valve", "edge_id": edge.id, "new_node_id": valve_node.id, "description": msg})
                        continue

            elif v.rule_code == "VAL-EQP-001":
                pump_node = diagram.node_by_id(getattr(v, 'node_id', None))
                if not pump_node:
                    continue
                new_tag = generate_sequential_tag(diagram, "CV")
                y_offset = NODE_Y_OFFSET.get("check_valve", DEFAULT_Y_OFFSET)
                free_x, free_y = _find_free_position(diagram.nodes, pump_node.position.x + 250, pump_node.position.y + y_offset)
                cv_node = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="check_valve",
                    tag=new_tag,
                    description="Check Valve",
                    position=Position(x=free_x, y=free_y)
                )
                diagram.nodes.append(cv_node)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS,
                    from_node=pump_node.id,
                    to_node=cv_node.id,
                    line_number=_next_line_number(diagram.edges)
                ))
                msg = f"{pump_node.tag} 토출측에 {new_tag} 체크밸브 추가"
                current_repairs.append({"action": "added_valve", "node_id": pump_node.id, "new_node_id": cv_node.id, "description": msg})
                continue

            elif v.rule_code == "VAL-EQP-002":
                pump_node = diagram.node_by_id(getattr(v, 'node_id', None))
                if not pump_node:
                    continue

                tag_in = generate_sequential_tag(diagram, "XV")
                y_offset_in = NODE_Y_OFFSET.get("gate_valve", DEFAULT_Y_OFFSET)
                free_x_in, free_y_in = _find_free_position(diagram.nodes, pump_node.position.x - 250, pump_node.position.y + y_offset_in, step=-250)
                gv_in = CanonicalNode(
                    type=NodeType.VALVE, subtype="gate_valve", tag=tag_in,
                    description="Suction Block Valve",
                    position=Position(x=free_x_in, y=free_y_in)
                )
                diagram.nodes.append(gv_in)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS, from_node=gv_in.id, to_node=pump_node.id,
                    line_number=_next_line_number(diagram.edges)
                ))

                tag_out = generate_sequential_tag(diagram, "XV")
                y_offset_out = NODE_Y_OFFSET.get("gate_valve", DEFAULT_Y_OFFSET)
                free_x_out, free_y_out = _find_free_position(diagram.nodes, pump_node.position.x + 500, pump_node.position.y + y_offset_out)
                gv_out = CanonicalNode(
                    type=NodeType.VALVE, subtype="gate_valve", tag=tag_out,
                    description="Discharge Block Valve",
                    position=Position(x=free_x_out, y=free_y_out)
                )
                diagram.nodes.append(gv_out)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS, from_node=pump_node.id, to_node=gv_out.id,
                    line_number=_next_line_number(diagram.edges)
                ))

                msg = f"{pump_node.tag} 흡입측 {tag_in}, 토출측 {tag_out} 차단밸브 추가"
                current_repairs.append({"action": "added_valve", "node_id": pump_node.id, "new_node_id": gv_in.id, "description": msg})
                continue

            elif v.rule_code == "VAL-EQP-003":
                vessel_node = diagram.node_by_id(getattr(v, 'node_id', None))
                if not vessel_node:
                    continue
                tag = generate_sequential_tag(diagram, "PSV")
                y_offset = NODE_Y_OFFSET.get("safety_valve", NODE_Y_OFFSET.get("relief_valve", -200))
                free_x, free_y = _find_free_position(diagram.nodes, vessel_node.position.x, vessel_node.position.y + y_offset)
                psv = CanonicalNode(
                    type=NodeType.VALVE, subtype="safety_valve", tag=tag,
                    description="Pressure Safety Valve",
                    position=Position(x=free_x, y=free_y)
                )
                diagram.nodes.append(psv)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS, from_node=vessel_node.id, to_node=psv.id,
                    line_number=_next_line_number(diagram.edges)
                ))
                msg = f"{vessel_node.tag}에 {tag} PSV 추가"
                current_repairs.append({"action": "added_psv", "node_id": vessel_node.id, "new_node_id": psv.id, "description": msg})
                continue

            elif v.rule_code == "VAL-EQP-005":
                pump_node = diagram.node_by_id(getattr(v, 'node_id', None))
                if not pump_node:
                    continue
                tag_cv = generate_sequential_tag(diagram, "FCV")
                y_offset = NODE_Y_OFFSET.get("control_valve", DEFAULT_Y_OFFSET)
                free_x, free_y = _find_free_position(diagram.nodes, pump_node.position.x, pump_node.position.y + y_offset)
                bypass_cv = CanonicalNode(
                    type=NodeType.VALVE, subtype="control_valve", tag=tag_cv,
                    description="Bypass Control Valve",
                    position=Position(x=free_x, y=free_y)
                )
                diagram.nodes.append(bypass_cv)

                upstream_id = next((e.from_node for e in diagram.edges if e.to_node == pump_node.id), None)
                downstream_id = next((e.to_node for e in diagram.edges if e.from_node == pump_node.id), None)

                if upstream_id and downstream_id:
                    diagram.edges.append(CanonicalEdge(
                        type=EdgeType.PROCESS, from_node=upstream_id, to_node=bypass_cv.id,
                        line_number=_next_line_number(diagram.edges)
                    ))
                    diagram.edges.append(CanonicalEdge(
                        type=EdgeType.PROCESS, from_node=bypass_cv.id, to_node=downstream_id,
                        line_number=_next_line_number(diagram.edges)
                    ))
                current_repairs.append({"action": "added_bypass", "node_id": pump_node.id, "new_node_id": bypass_cv.id, "description": f"{pump_node.tag} 바이패스 라인에 {tag_cv} 추가"})
                continue

            elif v.rule_code == "VAL-EQP-009":
                target_node = diagram.node_by_id(getattr(v, 'node_id', None))
                if not target_node:
                    continue

                tag_in = generate_sequential_tag(diagram, "XV")
                free_x_in, _ = _find_free_position(diagram.nodes, target_node.position.x - 250, target_node.position.y)
                xv_in = CanonicalNode(
                    type=NodeType.VALVE, subtype="gate_valve", tag=tag_in,
                    description="Gate Valve", location="field",
                    position=Position(x=free_x_in, y=target_node.position.y)
                )

                tag_out = generate_sequential_tag(diagram, "XV")
                free_x_out, _ = _find_free_position(diagram.nodes, target_node.position.x + 250, target_node.position.y)
                xv_out = CanonicalNode(
                    type=NodeType.VALVE, subtype="gate_valve", tag=tag_out,
                    description="Gate Valve", location="field",
                    position=Position(x=free_x_out, y=target_node.position.y)
                )

                for e in diagram.edges:
                    if e.to_node == target_node.id:
                        e.to_node = xv_in.id
                diagram.edges.append(CanonicalEdge(
                    from_node=xv_in.id, to_node=target_node.id,
                    type=EdgeType.PROCESS,
                    line_number=_next_line_number(diagram.edges), insulation="N"
                ))
                for e in diagram.edges:
                    if e.from_node == target_node.id:
                        e.from_node = xv_out.id
                diagram.edges.append(CanonicalEdge(
                    from_node=target_node.id, to_node=xv_out.id,
                    type=EdgeType.PROCESS,
                    line_number=_next_line_number(diagram.edges), insulation="N"
                ))

                diagram.nodes.append(xv_in)
                diagram.nodes.append(xv_out)
                current_repairs.append({"action": "added_valves", "node_id": target_node.id, "description": f"{target_node.tag} 전후에 {tag_in}, {tag_out} 차단밸브 추가"})
                continue

            elif v.rule_code == "isolated_node" and v.node_id:
                node = diagram.node_by_id(v.node_id)
                if node:
                    nearest = None
                    min_dist = float('inf')
                    for other in diagram.nodes:
                        if other.id != node.id and other.type == NodeType.EQUIPMENT:
                            dist = ((other.position.x - node.position.x) ** 2 + (other.position.y - node.position.y) ** 2) ** 0.5
                            if dist < min_dist:
                                min_dist = dist
                                nearest = other

                    if nearest:
                        diagram.edges.append(CanonicalEdge(
                            type=EdgeType.PROCESS,
                            from_node=node.id,
                            to_node=nearest.id,
                            line_number=_next_line_number(diagram.edges)
                        ))
                        msg = f"{node.tag} 노드를 {nearest.tag}에 연결"
                        current_repairs.append({"action": "connected_isolated_node", "node_id": node.id, "target_id": nearest.id, "description": msg})
                        continue

            unfixable.append(v)
            current_repairs.append({"action": "unrepairable", "description": f"수동 수정 필요: {v.rule_code}"})

        repairs_applied.extend(current_repairs)

        if rules is not None:
            report = validate(diagram, rules)
            if report.passed:
                remaining_violations = []
                break
            remaining_violations = report.violations
        else:
            remaining_violations = unfixable
            break

    # 레이아웃은 layout_engine을 통해 적용 (의존성 역전)
    diagram = layout_engine.apply_layout(diagram)
    return diagram, repairs_applied, remaining_violations
