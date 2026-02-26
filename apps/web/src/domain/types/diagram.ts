// domain/types/diagram.ts — 핵심 도메인 모델 (ReactFlow import 없음)

import type { NodeType, EdgeType } from "./enums";
import type { Position, Nozzle, EdgeProperties } from "./geometry";

export type { NodeType, EdgeType } from "./enums";
export type { Position, Nozzle, EdgeProperties } from "./geometry";

export interface CanonicalNode {
  id: string;
  type: NodeType;
  subtype: string;
  tag: string;
  name?: string;
  description?: string;
  location?: string;
  position: Position;
  properties: Record<string, unknown>;
  nozzles: Nozzle[];
}

export interface CanonicalEdge {
  id: string;
  type: EdgeType;
  from_node: string;
  from_port?: string;
  to_node: string;
  to_port?: string;
  line_number?: string;
  pipe_size?: string;
  pipe_class?: string;
  insulation?: string;
  properties: EdgeProperties;
  waypoints: Position[];
}

export interface CanonicalMetadata {
  area?: string;
  revision?: string;
  [key: string]: unknown;
}

export interface DiagramCanonical {
  canonical_schema_version: number;
  id?: string;
  name: string;
  diagram_type: "pfd" | "pid" | "bfd";
  project_id?: string;
  metadata: CanonicalMetadata;
  nodes: CanonicalNode[];
  edges: CanonicalEdge[];
}
