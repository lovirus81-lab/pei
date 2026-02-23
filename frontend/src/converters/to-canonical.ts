// frontend/src/converters/to-canonical.ts
// ReactFlow 상태 → Canonical JSON 변환 (저장/검증/내보내기 전 호출)

import type { Node, Edge } from "reactflow";
import type {
  DiagramCanonical,
  CanonicalNode,
  CanonicalEdge,
  NodeType,
  EdgeType,
} from "../types/canonical";

/**
 * ReactFlow 노드/엣지를 Canonical 도메인 스키마로 변환.
 * ReactFlow 전용 필드(selected, dragging, measured 등)는 제거한다.
 */
export function toCanonical(
  rfNodes: Node[],
  rfEdges: Edge[],
  meta: { id: string; name: string; project_id?: string; diagram_type?: "pfd" | "pid" | "bfd" }
): DiagramCanonical {
  const nodes: CanonicalNode[] = rfNodes.map((n) => {
    const data = n.data ?? {};
    return {
      id: n.id,
      type: (data.canonicalType ?? "equipment") as NodeType,
      subtype: data.subtype ?? "unknown",
      tag: data.label || data.tag || "",
      name: data.name,
      description: data.description || data.equipmentClass || "Equipment",
      location: data.location || "field",
      position: { x: n.position.x, y: n.position.y },
      properties: data.properties ?? {},
      nozzles: data.nozzles ?? [],
    };
  });

  const edges: CanonicalEdge[] = rfEdges.map((e) => {
    const data = e.data ?? {};
    return {
      id: e.id,
      type: (data.edgeType ?? "process") as EdgeType,
      from_node: e.source,
      from_port: e.sourceHandle ?? undefined,
      to_node: e.target,
      to_port: e.targetHandle || undefined,
      line_number: (e.label as string) || data.line_number || "",
      pipe_size: data.pipe_size,
      pipe_class: data.pipe_class,
      insulation: data.insulation || "N",
      properties: data.properties ?? {},
      waypoints: data.waypoints ?? [],
    };
  });

  return {
    canonical_schema_version: 1,
    id: meta.id,
    name: meta.name,
    diagram_type: meta.diagram_type ?? "pid",
    project_id: meta.project_id,
    nodes,
    edges,
    metadata: {},
  };
}
