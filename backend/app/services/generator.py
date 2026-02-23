from typing import List, Dict, Any, Tuple
from app.schemas.canonical import (
    DiagramCanonical, CanonicalNode, CanonicalEdge, NodeType, EdgeType, Position
)
from app.schemas.rules import Violation
from app.services.layout import apply_layout

EQUIPMENT_DESCRIPTIONS = {
    "storage_tank": "Storage Tank",
    "tank": "Storage Tank",
    "centrifugal_pump": "Centrifugal Pump",
    "vessel_vertical": "Vertical Vessel",
    "vessel_horizontal": "Horizontal Vessel",
    "vessel": "Storage Vessel",
    "heat_exchanger": "Heat Exchanger",
    "reactor": "Reactor",
    "distillation_column": "Distillation Column",
    "column": "Distillation Column",
    "control_valve": "Control Valve",
    "gate_valve": "Gate Valve",
    "check_valve": "Check Valve",
    "relief_valve": "Relief/Safety Valve",
    "safety_valve": "Relief/Safety Valve",
    "indicator_controller": "Indicator Controller"
}

NODE_Y_OFFSET = {
    "relief_valve": -200,       # PSV: 연결 장비 위
    "control_valve": -200,      # FCV bypass: 메인라인 위
    "temperature_indicator_controller": -150,
    "level_indicator_controller": -150,
    "flow_indicator_controller": -150,
    "pressure_indicator_controller": -150,
}
DEFAULT_Y_OFFSET = 0  # 메인라인 노드는 y 변경 없음


def _generate_sequential_tag(diagram: DiagramCanonical, prefix: str) -> str:
    max_num = 100
    for node in diagram.nodes:
        if node.tag and node.tag.startswith(f"{prefix}-"):
            try:
                num = int(node.tag.replace(f"{prefix}-", ""))
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"{prefix}-{max_num + 1}"

def generate_template(template_type: str) -> DiagramCanonical:
    """
    Generate a standard P&ID diagram configuration based on the requested template_type.
    Applies standard ISA tagging (e.g. Tank -> TK-101) and rules from GEN-EQP.
    """
    diagram = DiagramCanonical(name=f"Generated {template_type.replace('_', ' ').title()}")
    
    if template_type == "simple_pump_loop":
        # 1. Tank
        tank = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"),
            position=Position(x=100, y=200)
        )
        diagram.nodes.append(tank)
        
        # Pump Upstream Block Valve
        suction_block = CanonicalNode(
            type=NodeType.VALVE, subtype="gate_valve", tag=_generate_sequential_tag(diagram, "XV"),
            position=Position(x=350, y=200)
        )
        diagram.nodes.append(suction_block)

        # 2. Pump (with auto-added Block and Check Valves according to rules GEN-EQP-001/002)
        pump = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"),
            position=Position(x=600, y=200)
        )
        diagram.nodes.append(pump)
        
        # Pump Downstream Check Valve
        check_valve = CanonicalNode(
            type=NodeType.VALVE, subtype="check_valve", tag=_generate_sequential_tag(diagram, "XV"),
            position=Position(x=850, y=200)
        )
        diagram.nodes.append(check_valve)
        
        # Pump Downstream Block Valve
        discharge_block = CanonicalNode(
            type=NodeType.VALVE, subtype="gate_valve", tag=_generate_sequential_tag(diagram, "XV"),
            position=Position(x=1100, y=200)
        )
        diagram.nodes.append(discharge_block)
        
        # 3. Vessel
        vessel = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="vessel", tag=_generate_sequential_tag(diagram, "V"),
            position=Position(x=1350, y=200)
        )
        diagram.nodes.append(vessel)
        
        # Edges
        edges = [
            (tank.id, suction_block.id),
            (suction_block.id, pump.id),
            (pump.id, check_valve.id),
            (check_valve.id, discharge_block.id),
            (discharge_block.id, vessel.id)
        ]
        
        line_seq = 1
        for src, dst in edges:
            diagram.edges.append(CanonicalEdge(
                type=EdgeType.PROCESS, from_node=src, to_node=dst,
                line_number=f'2"-P-{100 + line_seq}-A1B'
            ))
            line_seq += 1
            
    elif template_type == "heat_exchange_unit":
        # 1. Nodes
        tank = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"), description="Storage Tank", position=Position(x=100, y=200))
        diagram.nodes.append(tank)
        pump = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"), description="Centrifugal Pump", position=Position(x=350, y=200))
        diagram.nodes.append(pump)
        he = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=_generate_sequential_tag(diagram, "HE"), description="Heat Exchanger", position=Position(x=600, y=200))
        diagram.nodes.append(he)
        cv = CanonicalNode(type=NodeType.VALVE, subtype="control_valve", tag=_generate_sequential_tag(diagram, "TV"), description="Control Valve", position=Position(x=850, y=200))
        diagram.nodes.append(cv)
        tic = CanonicalNode(type=NodeType.INSTRUMENT, subtype="indicator_controller", tag=_generate_sequential_tag(diagram, "TIC"), description="Temperature Controller", position=Position(x=850, y=50))
        diagram.nodes.append(tic)
        
        # 2. Edges
        process_edges = [(tank.id, pump.id), (pump.id, he.id), (he.id, cv.id)]
        for src, dst in process_edges:
            diagram.edges.append(CanonicalEdge(
                type=EdgeType.PROCESS, from_node=src, to_node=dst, line_number=_next_line_number(diagram.edges)
            ))
        
        diagram.edges.append(CanonicalEdge(
            type=EdgeType.SIGNAL_ELECTRICAL, from_node=tic.id, to_node=cv.id, line_number=_next_line_number(diagram.edges, fluid="S")
        ))

    elif template_type == "reactor_system":
        # 1. Nodes
        tank1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"), description="Storage Tank A", position=Position(x=100, y=100))
        diagram.nodes.append(tank1)
        tank2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"), description="Storage Tank B", position=Position(x=100, y=300))
        diagram.nodes.append(tank2)
        pump1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"), description="Feed Pump A", position=Position(x=350, y=100))
        diagram.nodes.append(pump1)
        pump2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"), description="Feed Pump B", position=Position(x=350, y=300))
        diagram.nodes.append(pump2)
        reactor = CanonicalNode(type=NodeType.EQUIPMENT, subtype="reactor", tag=_generate_sequential_tag(diagram, "R"), description="Chemical Reactor", position=Position(x=600, y=200))
        diagram.nodes.append(reactor)
        prv = CanonicalNode(type=NodeType.VALVE, subtype="safety_valve", tag=_generate_sequential_tag(diagram, "PRV"), description="Pressure Relief", position=Position(x=600, y=50))
        diagram.nodes.append(prv)
        lic = CanonicalNode(type=NodeType.INSTRUMENT, subtype="indicator_controller", tag=_generate_sequential_tag(diagram, "LIC"), description="Level Controller", position=Position(x=850, y=200))
        diagram.nodes.append(lic)
        
        # 2. Edges
        # Line 101
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=tank1.id, to_node=pump1.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=pump1.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges)))
        # Line 102
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=tank2.id, to_node=pump2.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=pump2.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges)))
        # PRV Line
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=reactor.id, to_node=prv.id, line_number=_next_line_number(diagram.edges)))
        # Signal Line
        diagram.edges.append(CanonicalEdge(type=EdgeType.SIGNAL_ELECTRICAL, from_node=lic.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges, fluid="S")))

    elif template_type == "distillation_basic":
        # 1. Nodes
        tank1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"), description="Feed Tank", position=Position(x=100, y=300))
        diagram.nodes.append(tank1)
        pump1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"), position=Position(x=350, y=300))
        diagram.nodes.append(pump1)
        he1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=_generate_sequential_tag(diagram, "HE"), position=Position(x=600, y=300))
        diagram.nodes.append(he1)
        col = CanonicalNode(type=NodeType.EQUIPMENT, subtype="column", tag=_generate_sequential_tag(diagram, "COL"), position=Position(x=850, y=300))
        diagram.nodes.append(col)
        he2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=_generate_sequential_tag(diagram, "HE"), position=Position(x=850, y=100))
        diagram.nodes.append(he2)
        tank2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=_generate_sequential_tag(diagram, "TK"), position=Position(x=1100, y=100))
        diagram.nodes.append(tank2)
        pump2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=_generate_sequential_tag(diagram, "P"), position=Position(x=1100, y=300))
        diagram.nodes.append(pump2)
        
        # 2. Edges
        # Feed Line
        for src, dst in [(tank1.id, pump1.id), (pump1.id, he1.id), (he1.id, col.id)]:
            diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=src, to_node=dst, line_number=_next_line_number(diagram.edges)))
        
        # Reflux Line
        for src, dst in [(col.id, he2.id), (he2.id, tank2.id), (tank2.id, pump2.id), (pump2.id, col.id)]:
            diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=src, to_node=dst, line_number=_next_line_number(diagram.edges, size="4\"", fluid="R")))

    else:
        raise ValueError(f"Unknown template_type: {template_type}")

    for node in diagram.nodes:
        if not node.description:
            node.description = EQUIPMENT_DESCRIPTIONS.get(node.subtype, node.subtype.replace("_", " ").title())

    diagram = apply_layout(diagram)
    return diagram


def _next_line_number(edges: list, fluid="P", size='2"', cls="A1B") -> str:
    existing_seqs = []
    for e in edges:
        if getattr(e, 'line_number', None):
            parts = e.line_number.split("-")
            if len(parts) >= 3 and parts[-2].isdigit():
                existing_seqs.append(int(parts[-2]))
    seq = max(existing_seqs, default=100) + 1
    return f'{size}-{fluid}-{seq:03d}-{cls}'

def _find_free_position(nodes, base_x, base_y, step=250):
    occupied = {(n.position.x, n.position.y) for n in nodes}
    x = base_x
    while (x, base_y) in occupied:
        x += step
    return x, base_y

def auto_repair(diagram: DiagramCanonical, violations: List[Violation], rules: List[Any] = None) -> Tuple[DiagramCanonical, List[Dict[str, Any]], List[Violation]]:
    """
    Applies automatic rectifications to a diagram based on violations reported by the validator.
    Returns (RepairedDiagram, AppliedRepairsList, UnfixableViolationsList)
    """
    from app.services.validator import validate

    repairs_applied = []
    remaining_violations = violations
    
    max_iterations = 3
    for iteration in range(max_iterations):
        if not remaining_violations:
            break
            
        current_repairs = []
        unfixable = []
        
        for v in remaining_violations:
            with open("debug_repair.log", "a") as f:
                f.write(f"[repair] rule_id={getattr(v, 'rule_id', None)}, rule_code={getattr(v, 'rule_code', None)}, node_id={getattr(v, 'node_id', None)}\n")
            if v.rule_code == "missing_instrument" and v.node_id:
                node = diagram.node_by_id(v.node_id)
                if node:
                    subtype = "indicator_controller"
                    prefix = "IC"
                    if node.subtype in ("pump", "centrifugal_pump"): prefix = "FIC"
                    elif node.subtype in ("vessel", "tank"): prefix = "LIC"
                    elif node.subtype == "heat_exchanger": prefix = "TIC"
                    
                    inst_tag = _generate_sequential_tag(diagram, prefix)
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
                    
                    signal_edge = CanonicalEdge(
                        type=EdgeType.SIGNAL_ELECTRICAL,
                        from_node=inst_node.id,
                        to_node=node.id,
                        line_number=f"S-{inst_tag}"
                    )
                    diagram.edges.append(signal_edge)
                    
                    msg = f"{node.tag}에 {inst_tag} 계기 추가"
                    current_repairs.append({"action": "added_instrument", "node_id": node.id, "new_node_id": inst_node.id, "description": msg})
                    continue
                    
            elif v.rule_code == "missing_valve" and v.edge_id:
                edge = next((e for e in diagram.edges if e.id == v.edge_id), None)
                if edge:
                    src_node = diagram.node_by_id(edge.from_node)
                    tgt_node = diagram.node_by_id(edge.to_node)
                    if src_node and tgt_node:
                        v_tag = _generate_sequential_tag(diagram, "XV")
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
                
                # 엣지 유무 무관하게 check_valve 노드 생성
                new_tag = _generate_sequential_tag(diagram, "CV")
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
                
                # pump → cv 엣지 생성
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
                
                # 흡입측 gate_valve
                tag_in = _generate_sequential_tag(diagram, "XV")
                y_offset_in = NODE_Y_OFFSET.get("gate_valve", DEFAULT_Y_OFFSET)
                free_x_in, free_y_in = _find_free_position(diagram.nodes, pump_node.position.x - 250, pump_node.position.y + y_offset_in, step=-250)
                gv_in = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="gate_valve",
                    tag=tag_in,
                    description="Suction Block Valve",
                    position=Position(x=free_x_in, y=free_y_in)
                )
                diagram.nodes.append(gv_in)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS,
                    from_node=gv_in.id,
                    to_node=pump_node.id,
                    line_number=_next_line_number(diagram.edges)
                ))
                
                # 토출측 gate_valve
                tag_out = _generate_sequential_tag(diagram, "XV")
                y_offset_out = NODE_Y_OFFSET.get("gate_valve", DEFAULT_Y_OFFSET)
                free_x_out, free_y_out = _find_free_position(diagram.nodes, pump_node.position.x + 500, pump_node.position.y + y_offset_out)
                gv_out = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="gate_valve",
                    tag=tag_out,
                    description="Discharge Block Valve",
                    position=Position(x=free_x_out, y=free_y_out)
                )
                diagram.nodes.append(gv_out)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS,
                    from_node=pump_node.id,
                    to_node=gv_out.id,
                    line_number=_next_line_number(diagram.edges)
                ))
                
                msg = f"{pump_node.tag} 흡입측 {tag_in}, 토출측 {tag_out} 차단밸브 추가"
                current_repairs.append({"action": "added_valve", "node_id": pump_node.id, "new_node_id": gv_in.id, "description": msg})
                continue

            elif v.rule_code == "VAL-EQP-003":
                vessel_node = next((n for n in diagram.nodes if n.id == v.node_id), None)
                if not vessel_node:
                    continue
                tag = _generate_sequential_tag(diagram, "PSV")
                y_offset = NODE_Y_OFFSET.get("safety_valve", DEFAULT_Y_OFFSET) # "safety_valve" not in dict, user said "relief_valve": -200, so fallback... wait, I should add "safety_valve": -200 to dict just in case. Let me use -200 explicitly to match user request "PSV: 연결 장비 위".
                if "safety_valve" not in NODE_Y_OFFSET and "relief_valve" in NODE_Y_OFFSET:
                    NODE_Y_OFFSET["safety_valve"] = NODE_Y_OFFSET["relief_valve"]
                y_offset = NODE_Y_OFFSET.get("safety_valve", DEFAULT_Y_OFFSET)
                free_x, free_y = _find_free_position(diagram.nodes, vessel_node.position.x, vessel_node.position.y + y_offset)
                psv = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="safety_valve",
                    tag=tag,
                    description="Pressure Safety Valve",
                    position=Position(x=free_x, y=free_y)
                )
                diagram.nodes.append(psv)
                diagram.edges.append(CanonicalEdge(
                    type=EdgeType.PROCESS,
                    from_node=vessel_node.id,
                    to_node=psv.id,
                    line_number=_next_line_number(diagram.edges)
                ))
                msg = f"{vessel_node.tag}에 {tag} PSV 추가"
                current_repairs.append({"action": "added_psv", "node_id": vessel_node.id, "new_node_id": psv.id, "description": msg})
                continue
                
            elif v.rule_code == "VAL-EQP-005":
                pump_node = next((n for n in diagram.nodes if n.id == v.node_id), None)
                if not pump_node:
                    continue
                # 바이패스: pump 상류 → control_valve → pump 하류 병렬 경로
                tag_cv = _generate_sequential_tag(diagram, "FCV")
                y_offset = NODE_Y_OFFSET.get("control_valve", DEFAULT_Y_OFFSET)
                free_x, free_y = _find_free_position(diagram.nodes, pump_node.position.x, pump_node.position.y + y_offset)
                bypass_cv = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="control_valve",
                    tag=tag_cv,
                    description="Bypass Control Valve",
                    position=Position(
                        x=free_x,
                        y=free_y
                    )
                )
                diagram.nodes.append(bypass_cv)

                # 상류 노드 탐색 (pump incoming 엣지 source)
                upstream_id = next(
                    (e.from_node for e in diagram.edges if e.to_node == pump_node.id),
                    None
                )
                # 하류 노드 탐색 (pump outgoing 엣지 target)
                downstream_id = next(
                    (e.to_node for e in diagram.edges if e.from_node == pump_node.id),
                    None
                )

                if upstream_id and downstream_id:
                    edge1 = CanonicalEdge(
                        type=EdgeType.PROCESS,
                        from_node=upstream_id,
                        to_node=bypass_cv.id,
                        line_number=_next_line_number(diagram.edges)
                    )
                    diagram.edges.append(edge1)
                    edge2 = CanonicalEdge(
                        type=EdgeType.PROCESS,
                        from_node=bypass_cv.id,
                        to_node=downstream_id,
                        line_number=_next_line_number(diagram.edges)
                    )
                    diagram.edges.append(edge2)
                msg = f"{pump_node.tag} 바이패스 라인에 {tag_cv} 추가"
                continue

            elif v.rule_code == "VAL-EQP-009":
                target_node = next((n for n in diagram.nodes if n.id == v.node_id), None)
                if not target_node:
                    continue

                # 상류 차단밸브
                tag_in = _generate_sequential_tag(diagram, "XV")
                free_x_in, _ = _find_free_position(diagram.nodes, target_node.position.x - 250, target_node.position.y)
                xv_in = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="gate_valve",
                    tag=tag_in,
                    description="Gate Valve",
                    location="field",
                    position=Position(x=free_x_in, y=target_node.position.y)
                )

                # 하류 차단밸브
                tag_out = _generate_sequential_tag(diagram, "XV")
                free_x_out, _ = _find_free_position(diagram.nodes, target_node.position.x + 250, target_node.position.y)
                xv_out = CanonicalNode(
                    type=NodeType.VALVE,
                    subtype="gate_valve",
                    tag=tag_out,
                    description="Gate Valve",
                    location="field",
                    position=Position(x=free_x_out, y=target_node.position.y)
                )

                # 기존 incoming/outgoing 엣지 재연결
                incoming = [e for e in diagram.edges if e.to_node == target_node.id]
                outgoing = [e for e in diagram.edges if e.from_node == target_node.id]

                for e in incoming:
                    e.to_node = xv_in.id
                diagram.edges.append(CanonicalEdge(
                    from_node=xv_in.id,
                    to_node=target_node.id,
                    type=EdgeType.PROCESS,
                    line_number=_next_line_number(diagram.edges),
                    insulation="N"
                ))

                for e in outgoing:
                    e.from_node = xv_out.id
                diagram.edges.append(CanonicalEdge(
                    from_node=target_node.id,
                    to_node=xv_out.id,
                    type=EdgeType.PROCESS,
                    line_number=_next_line_number(diagram.edges),
                    insulation="N"
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
                            dist = ((other.position.x - node.position.x)**2 + (other.position.y - node.position.y)**2)**0.5
                            if dist < min_dist:
                                min_dist = dist
                                nearest = other
                    
                    if nearest:
                        new_edge = CanonicalEdge(
                            type=EdgeType.PROCESS,
                            from_node=node.id,
                            to_node=nearest.id,
                            line_number=_next_line_number(diagram.edges)
                        )
                        diagram.edges.append(new_edge)
                        
                        msg = f"{node.tag} 노드를 {nearest.tag}에 연결"
                        current_repairs.append({"action": "connected_isolated_node", "node_id": node.id, "target_id": nearest.id, "description": msg})
                        continue

            unfixable.append(v)
            current_repairs.append({"action": "unrepairable", "description": f"수동 수정 필요: {v.rule_code}"})

        repairs_applied.extend(current_repairs)
        
        if rules is not None:
            # Re-validate
            report = validate(diagram, rules)
            if report.passed:
                remaining_violations = []
                break
            remaining_violations = report.violations
        else:
            remaining_violations = unfixable
            break

    diagram = apply_layout(diagram)
    return diagram, repairs_applied, remaining_violations


def ai_assist(diagram: DiagramCanonical, request: str) -> Dict[str, Any]:
    """
    Takes a natural language query and uses an AI broker to suggest/apply modifications to the diagram.
    Currently stubbed out as a skeleton.
    """
    # Skeleton AI Logic
    return {
        "suggestions": [
            {
                "description": f"AI perceived request: '{request}'. Suggesting insertion of Flow Transmitter.",
                "confidence": 0.85
            }
        ],
        "auto_applicable": True,
        "modified_diagram": None # Usually would return a mutated diagram if auto_applicable was resolved.
    }
