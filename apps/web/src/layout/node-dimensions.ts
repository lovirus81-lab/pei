// layout/node-dimensions.ts — 노드 타입별 크기 (layout 계층)

import type { NodeType } from "../domain/types/enums";

export interface NodeDimension {
  width: number;
  height: number;
}

export const NODE_DIMENSIONS: Record<NodeType | string, NodeDimension> = {
  equipment: { width: 80, height: 80 },
  valve: { width: 60, height: 60 },
  instrument: { width: 60, height: 60 },
  fitting: { width: 40, height: 40 },
};

export function getNodeDimension(nodeType: string): NodeDimension {
  return NODE_DIMENSIONS[nodeType] ?? NODE_DIMENSIONS.equipment;
}
