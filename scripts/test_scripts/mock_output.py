import asyncio
import sys
from app.schemas.canonical import DiagramCanonical, CanonicalNode, CanonicalEdge, Position, NodeType, EdgeType

node = CanonicalNode(
    id="n1",
    type=NodeType.EQUIPMENT,
    subtype="centrifugal_pump",
    tag="P-101",
    description="Equipment",
    position=Position(x=0, y=0)
)
edge = CanonicalEdge(
    id="e1",
    from_node="n1",
    to_node="n2",
    type=EdgeType.PROCESS,
    line_number="2\"-P-101-A1B",
    insulation="N"
)

print(f"[CMP-002] tag={node.tag} desc='{node.description}' type={type(node.description)}")
print(f"[PIP-007] line={edge.line_number} insulation='{edge.insulation}' type={type(edge.insulation)}")
