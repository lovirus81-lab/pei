// layout/elk-adapter.ts — DiagramCanonical ↔ ELK 그래프 변환 (layout 계층)

import type { DiagramCanonical, CanonicalNode } from "../domain/types/diagram";
import { getNodeDimension } from "./node-dimensions";
import { nozzleToElkPort } from "./elk-port-mapper";

// elkjs 내장 타입 (any로 타이핑하는 대신 필요한 부분만 정의)
interface ElkNodeDef {
  id: string;
  width?: number;
  height?: number;
  layoutOptions?: Record<string, string>;
  ports?: { id: string; layoutOptions?: Record<string, string> }[];
}

interface ElkEdgeDef {
  id: string;
  sources: string[];
  targets: string[];
}

export interface ElkGraphDef {
  id: string;
  layoutOptions: Record<string, string>;
  children: ElkNodeDef[];
  edges: ElkEdgeDef[];
}

/**
 * DiagramCanonical → ELK 그래프 빌드.
 * 노즐이 있으면 포트로 매핑, 없으면 4방향 기본 포트 사용.
 */
export function buildElkGraph(diagram: DiagramCanonical): ElkGraphDef {
  return {
    id: "root",
    layoutOptions: {
      "elk.algorithm": "org.eclipse.elk.layered",
      "elk.direction": "RIGHT",
      "elk.layered.spacing.nodeNodeBetweenLayers": "100",
      "elk.spacing.nodeNode": "80",
      "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
      "elk.edgeRouting": "ORTHOGONAL",
    },
    children: diagram.nodes.map((node) => {
      const dims = getNodeDimension(node.type);
      const ports =
        node.nozzles && node.nozzles.length > 0
          ? node.nozzles.map(nozzleToElkPort)
          : _defaultPorts(node, dims);

      return {
        id: node.id,
        width: dims.width,
        height: dims.height,
        layoutOptions: { "elk.portConstraints": "FIXED_SIDE" },
        ports,
      };
    }),
    edges: diagram.edges.map((edge) => ({
      id: edge.id,
      sources: [
        edge.from_port
          ? edge.from_port
          : `${edge.from_node}__right`,
      ],
      targets: [
        edge.to_port
          ? edge.to_port
          : `${edge.to_node}__left`,
      ],
    })),
  };
}

/** 노즐이 없는 노드용 기본 4방향 포트 */
function _defaultPorts(
  node: CanonicalNode,
  dims: { width: number; height: number }
) {
  return [
    { id: `${node.id}__left`, layoutOptions: { "elk.port.side": "WEST" } },
    { id: `${node.id}__right`, layoutOptions: { "elk.port.side": "EAST" } },
    { id: `${node.id}__top`, layoutOptions: { "elk.port.side": "NORTH" } },
    { id: `${node.id}__bottom`, layoutOptions: { "elk.port.side": "SOUTH" } },
  ];
}

/**
 * ELK 레이아웃 결과에서 노드 위치를 추출해 DiagramCanonical을 업데이트한다.
 */
export function extractPositions(
  original: DiagramCanonical,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  laidOut: any
): DiagramCanonical {
  const posMap = new Map<string, { x: number; y: number }>();

  for (const child of laidOut.children ?? []) {
    if (child.x !== undefined && child.y !== undefined) {
      posMap.set(child.id, { x: child.x, y: child.y });
    }
  }

  return {
    ...original,
    nodes: original.nodes.map((node) => ({
      ...node,
      position: posMap.get(node.id) ?? node.position,
    })),
  };
}
