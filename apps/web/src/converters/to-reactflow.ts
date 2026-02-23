// frontend/src/converters/to-reactflow.ts
// Canonical JSON → ReactFlow 노드/엣지 변환 (DB 로드 후 렌더링 전 호출)

import type { Node, Edge } from "reactflow";
import { MarkerType } from "reactflow";
import type {
  DiagramCanonical,
  CanonicalNode,
  CanonicalEdge,
  EdgeType,
} from "../types/canonical";

// 엣지 타입별 스타일 매핑
const EDGE_STYLES: Record<EdgeType, React.CSSProperties & { strokeDasharray?: string }> = {
  process: { stroke: "#000", strokeWidth: 2 },
  utility: { stroke: "#000", strokeWidth: 1.5, strokeDasharray: "6 3" },
  signal_electrical: { stroke: "#000", strokeWidth: 1, strokeDasharray: "2 2" },
  signal_pneumatic: { stroke: "#000", strokeWidth: 1, strokeDasharray: "2 2" },
};

const SUBTYPE_TO_SYMBOL: Record<string, string> = {
  vessel: "vessel_vertical",
  indicator_controller: "field_mounted",
};

function canonicalNodeToRF(node: CanonicalNode): Node {
  const symbolKey = SUBTYPE_TO_SYMBOL[node.subtype] || node.subtype;

  return {
    id: node.id,
    type: "pid",                        // 수정됨: pidNode -> pid
    position: node.position,
    data: {
      canonicalType: node.type,
      subtype: node.subtype,
      tag: node.tag,
      name: node.name,
      properties: node.properties,
      nozzles: node.nozzles,

      // UI 렌더링을 위해 PidNode가 기대하는 도메인 데이터
      symbolId: symbolKey,
      equipmentClass: symbolKey,
      label: node.tag || node.subtype,
      location: node.location ?? "field",
      description: node.description ?? "",
    },
  };
}

function canonicalEdgeToRF(edge: CanonicalEdge): Edge {
  const style = (edge.type ? EDGE_STYLES[edge.type] : undefined) ?? EDGE_STYLES.process;

  return {
    id: edge.id,
    source: edge.from_node,
    sourceHandle: edge.from_port ?? "right-source",
    target: edge.to_node,
    targetHandle: edge.to_port ?? "left-target",
    type: "smoothstep",

    // ⚠️ DO NOT REMOVE: label must be set from line_number for P&ID rendering
    label: edge.line_number && edge.line_number !== "" ? edge.line_number : undefined,
    labelStyle: { fontSize: 11, fill: "#444" },
    labelBgPadding: [4, 2] as [number, number],
    labelBgStyle: { fill: "#fff", fillOpacity: 0.85 },

    style: edge.type === "signal_electrical" || edge.type === "signal_pneumatic"
      ? { strokeDasharray: "5,5", stroke: "#888" }
      : style,
    markerEnd: { type: MarkerType.Arrow, width: 12, height: 12 },
    data: {
      edgeType: edge.type,
      line_number: edge.line_number,
      insulation: edge.insulation ?? "N",
      pipe_size: edge.pipe_size ?? '2"',
      pipe_class: edge.pipe_class ?? "A1B",
      properties: edge.properties,
      waypoints: edge.waypoints,
    },
  };
}

/**
 * Canonical 도면 → ReactFlow 렌더링 데이터로 변환.
 * 도메인 데이터는 node.data / edge.data 안에 그대로 보존한다.
 */
export function toReactFlow(canonical: DiagramCanonical): {
  nodes: Node[];
  edges: Edge[];
} {
  return {
    nodes: canonical.nodes.map(canonicalNodeToRF),
    edges: canonical.edges.map(canonicalEdgeToRF),
  };
}
