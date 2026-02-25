"""도메인 핵심 모델 — 단일 P&ID 도면의 정규 표현"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.domain.models.enums import NodeType, EdgeType
from app.domain.models.geometry import Position, Nozzle, EdgeProperties


class CanonicalNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: NodeType
    subtype: str                        # e.g., "centrifugal_pump", "check_valve"
    tag: str                            # e.g., "P-101", "TIC-1001"
    name: str | None = None
    description: str | None = None
    position: Position
    location: str | None = "field"
    properties: dict[str, Any] = Field(default_factory=dict)
    nozzles: list[Nozzle] = Field(default_factory=list)


class CanonicalEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EdgeType = EdgeType.PROCESS
    from_node: str                      # CanonicalNode.id
    from_port: str | None = None        # Nozzle.id
    to_node: str
    to_port: str | None = None
    line_number: str | None = None      # e.g., '6"-PLA-001-A2A'
    pipe_size: str | None = None        # e.g., '2"'
    pipe_class: str | None = None       # e.g., "A1B"
    insulation: str | None = "N"        # e.g., "H"
    properties: EdgeProperties = Field(default_factory=EdgeProperties)
    waypoints: list[Position] = Field(default_factory=list)


class DiagramCanonical(BaseModel):
    """단일 P&ID 도면의 Canonical 표현. DB 저장 기준."""
    canonical_schema_version: int = 1
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    diagram_type: str = "pid"           # "pfd" | "pid" | "bfd"
    project_id: str | None = None
    nodes: list[CanonicalNode] = Field(default_factory=list)
    edges: list[CanonicalEdge] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def node_by_id(self, node_id: str) -> CanonicalNode | None:
        return next((n for n in self.nodes if n.id == node_id), None)

    def edges_from(self, node_id: str) -> list[CanonicalEdge]:
        return [e for e in self.edges if e.from_node == node_id]

    def edges_to(self, node_id: str) -> list[CanonicalEdge]:
        return [e for e in self.edges if e.to_node == node_id]

    def downstream_nodes(self, node_id: str) -> list[CanonicalNode]:
        """직접 연결된 하류 노드 목록"""
        return [n for e in self.edges_from(node_id)
                if (n := self.node_by_id(e.to_node)) is not None]

    def upstream_nodes(self, node_id: str) -> list[CanonicalNode]:
        """직접 연결된 상류 노드 목록"""
        return [n for e in self.edges_to(node_id)
                if (n := self.node_by_id(e.from_node)) is not None]
