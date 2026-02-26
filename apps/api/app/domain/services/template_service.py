"""템플릿 생성 서비스 — 순수 도메인 로직, 레이아웃 호출 없음"""
from __future__ import annotations

from app.domain.models.diagram import DiagramCanonical, CanonicalNode, CanonicalEdge
from app.domain.models.enums import NodeType, EdgeType
from app.domain.models.geometry import Position
from app.domain.services.tag_service import generate_sequential_tag

EQUIPMENT_DESCRIPTIONS: dict[str, str] = {
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


def _next_line_number(edges: list, fluid: str = "P", size: str = '2"', cls: str = "A1B") -> str:
    existing_seqs = []
    for e in edges:
        if getattr(e, 'line_number', None):
            parts = e.line_number.split("-")
            if len(parts) >= 3 and parts[-2].isdigit():
                existing_seqs.append(int(parts[-2]))
    seq = max(existing_seqs, default=100) + 1
    return f'{size}-{fluid}-{seq:03d}-{cls}'


def generate_template(template_type: str) -> DiagramCanonical:
    """
    표준 P&ID 도면 템플릿을 생성한다.
    레이아웃(Position 계산)은 포함하지 않음 — 호출자가 레이아웃 엔진을 적용한다.
    """
    diagram = DiagramCanonical(name=f"Generated {template_type.replace('_', ' ').title()}")

    if template_type == "simple_pump_loop":
        tank = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="tank",
            tag=generate_sequential_tag(diagram, "TK"),
            position=Position(x=100, y=200)
        )
        diagram.nodes.append(tank)

        suction_block = CanonicalNode(
            type=NodeType.VALVE, subtype="gate_valve",
            tag=generate_sequential_tag(diagram, "XV"),
            position=Position(x=350, y=200)
        )
        diagram.nodes.append(suction_block)

        pump = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="centrifugal_pump",
            tag=generate_sequential_tag(diagram, "P"),
            position=Position(x=600, y=200)
        )
        diagram.nodes.append(pump)

        check_valve = CanonicalNode(
            type=NodeType.VALVE, subtype="check_valve",
            tag=generate_sequential_tag(diagram, "XV"),
            position=Position(x=850, y=200)
        )
        diagram.nodes.append(check_valve)

        discharge_block = CanonicalNode(
            type=NodeType.VALVE, subtype="gate_valve",
            tag=generate_sequential_tag(diagram, "XV"),
            position=Position(x=1100, y=200)
        )
        diagram.nodes.append(discharge_block)

        vessel = CanonicalNode(
            type=NodeType.EQUIPMENT, subtype="vessel",
            tag=generate_sequential_tag(diagram, "V"),
            position=Position(x=1350, y=200)
        )
        diagram.nodes.append(vessel)

        edges = [
            (tank.id, suction_block.id),
            (suction_block.id, pump.id),
            (pump.id, check_valve.id),
            (check_valve.id, discharge_block.id),
            (discharge_block.id, vessel.id)
        ]
        for i, (src, dst) in enumerate(edges, 1):
            diagram.edges.append(CanonicalEdge(
                type=EdgeType.PROCESS, from_node=src, to_node=dst,
                line_number=f'2"-P-{100 + i}-A1B'
            ))

    elif template_type == "heat_exchange_unit":
        tank = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=generate_sequential_tag(diagram, "TK"), description="Storage Tank", position=Position(x=100, y=200))
        diagram.nodes.append(tank)
        pump = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=generate_sequential_tag(diagram, "P"), description="Centrifugal Pump", position=Position(x=350, y=200))
        diagram.nodes.append(pump)
        he = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=generate_sequential_tag(diagram, "HE"), description="Heat Exchanger", position=Position(x=600, y=200))
        diagram.nodes.append(he)
        cv = CanonicalNode(type=NodeType.VALVE, subtype="control_valve", tag=generate_sequential_tag(diagram, "TV"), description="Control Valve", position=Position(x=850, y=200))
        diagram.nodes.append(cv)
        tic = CanonicalNode(type=NodeType.INSTRUMENT, subtype="indicator_controller", tag=generate_sequential_tag(diagram, "TIC"), description="Temperature Controller", position=Position(x=850, y=50))
        diagram.nodes.append(tic)

        for src, dst in [(tank.id, pump.id), (pump.id, he.id), (he.id, cv.id)]:
            diagram.edges.append(CanonicalEdge(
                type=EdgeType.PROCESS, from_node=src, to_node=dst,
                line_number=_next_line_number(diagram.edges)
            ))

        diagram.edges.append(CanonicalEdge(
            type=EdgeType.SIGNAL_ELECTRICAL, from_node=tic.id, to_node=cv.id,
            line_number=_next_line_number(diagram.edges, fluid="S")
        ))

    elif template_type == "reactor_system":
        tank1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=generate_sequential_tag(diagram, "TK"), description="Storage Tank A", position=Position(x=100, y=100))
        diagram.nodes.append(tank1)
        tank2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=generate_sequential_tag(diagram, "TK"), description="Storage Tank B", position=Position(x=100, y=300))
        diagram.nodes.append(tank2)
        pump1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=generate_sequential_tag(diagram, "P"), description="Feed Pump A", position=Position(x=350, y=100))
        diagram.nodes.append(pump1)
        pump2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=generate_sequential_tag(diagram, "P"), description="Feed Pump B", position=Position(x=350, y=300))
        diagram.nodes.append(pump2)
        reactor = CanonicalNode(type=NodeType.EQUIPMENT, subtype="reactor", tag=generate_sequential_tag(diagram, "R"), description="Chemical Reactor", position=Position(x=600, y=200))
        diagram.nodes.append(reactor)
        prv = CanonicalNode(type=NodeType.VALVE, subtype="safety_valve", tag=generate_sequential_tag(diagram, "PRV"), description="Pressure Relief", position=Position(x=600, y=50))
        diagram.nodes.append(prv)
        lic = CanonicalNode(type=NodeType.INSTRUMENT, subtype="indicator_controller", tag=generate_sequential_tag(diagram, "LIC"), description="Level Controller", position=Position(x=850, y=200))
        diagram.nodes.append(lic)

        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=tank1.id, to_node=pump1.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=pump1.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=tank2.id, to_node=pump2.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=pump2.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=reactor.id, to_node=prv.id, line_number=_next_line_number(diagram.edges)))
        diagram.edges.append(CanonicalEdge(type=EdgeType.SIGNAL_ELECTRICAL, from_node=lic.id, to_node=reactor.id, line_number=_next_line_number(diagram.edges, fluid="S")))

    elif template_type == "distillation_basic":
        tank1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=generate_sequential_tag(diagram, "TK"), description="Feed Tank", position=Position(x=100, y=300))
        diagram.nodes.append(tank1)
        pump1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=generate_sequential_tag(diagram, "P"), position=Position(x=350, y=300))
        diagram.nodes.append(pump1)
        he1 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=generate_sequential_tag(diagram, "HE"), position=Position(x=600, y=300))
        diagram.nodes.append(he1)
        col = CanonicalNode(type=NodeType.EQUIPMENT, subtype="column", tag=generate_sequential_tag(diagram, "COL"), position=Position(x=850, y=300))
        diagram.nodes.append(col)
        he2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="heat_exchanger", tag=generate_sequential_tag(diagram, "HE"), position=Position(x=850, y=100))
        diagram.nodes.append(he2)
        tank2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="tank", tag=generate_sequential_tag(diagram, "TK"), position=Position(x=1100, y=100))
        diagram.nodes.append(tank2)
        pump2 = CanonicalNode(type=NodeType.EQUIPMENT, subtype="centrifugal_pump", tag=generate_sequential_tag(diagram, "P"), position=Position(x=1100, y=300))
        diagram.nodes.append(pump2)

        for src, dst in [(tank1.id, pump1.id), (pump1.id, he1.id), (he1.id, col.id)]:
            diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=src, to_node=dst, line_number=_next_line_number(diagram.edges)))

        for src, dst in [(col.id, he2.id), (he2.id, tank2.id), (tank2.id, pump2.id), (pump2.id, col.id)]:
            diagram.edges.append(CanonicalEdge(type=EdgeType.PROCESS, from_node=src, to_node=dst, line_number=_next_line_number(diagram.edges, size='4"', fluid="R")))

    else:
        raise ValueError(f"Unknown template_type: {template_type}")

    # 설명이 없는 노드에 기본값 설정
    for node in diagram.nodes:
        if not node.description:
            node.description = EQUIPMENT_DESCRIPTIONS.get(node.subtype, node.subtype.replace("_", " ").title())

    # 레이아웃은 호출자가 적용 (template_service는 위치 계산에 관여하지 않음)
    return diagram
