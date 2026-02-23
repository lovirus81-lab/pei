# backend/app/schemas/converters.py
# Canonical ↔ UI(ReactFlow) 변환 — 백엔드에서 API 응답 직렬화 시 사용

from __future__ import annotations

from .canonical import (
    CanonicalEdge,
    CanonicalNode,
    DiagramCanonical,
    EdgeProperties,
    EdgeType,
    NodeType,
    Position,
)


def ui_to_canonical(ui_json: dict) -> DiagramCanonical:
    """
    프론트엔드가 보낸 ReactFlow JSON → DiagramCanonical.
    프론트의 to-canonical.ts 결과물을 백엔드에서 재검증한다.
    """
    nodes = [
        CanonicalNode(
            id=n["id"],
            type=NodeType(n.get("type", "equipment")),
            subtype=n.get("subtype", "unknown"),
            tag=n.get("tag", ""),
            name=n.get("name"),
            position=Position(**n["position"]),
            properties=n.get("properties", {}),
            nozzles=n.get("nozzles", []),
        )
        for n in ui_json.get("nodes", [])
    ]

    edges = [
        CanonicalEdge(
            id=e["id"],
            type=EdgeType(e.get("type", "process")),
            from_node=e["from_node"],
            from_port=e.get("from_port"),
            to_node=e["to_node"],
            to_port=e.get("to_port"),
            line_number=e.get("line_number"),
            properties=EdgeProperties(**e.get("properties", {})),
            waypoints=[Position(**p) for p in e.get("waypoints", [])],
        )
        for e in ui_json.get("edges", [])
    ]

    return DiagramCanonical(
        canonical_schema_version=1,
        id=ui_json["id"],
        name=ui_json["name"],
        diagram_type=ui_json.get("diagram_type", "pid"),
        project_id=ui_json.get("project_id"),
        nodes=nodes,
        edges=edges,
        metadata=ui_json.get("metadata", {}),
    )


def canonical_to_ui(canonical: DiagramCanonical) -> dict:
    """
    DiagramCanonical → 프론트엔드 전송용 dict.
    ReactFlow 스타일 필드는 프론트의 to-reactflow.ts가 처리하므로
    여기서는 순수 Canonical JSON만 반환한다.
    """
    return canonical.model_dump()
