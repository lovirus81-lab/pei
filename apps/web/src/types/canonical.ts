// frontend/src/types/canonical.ts

export type NodeType = "equipment" | "valve" | "instrument" | "fitting";

export type EdgeType =
  | "process"
  | "utility"
  | "signal_electrical"
  | "signal_pneumatic";

export type EquipmentSubtype =
  | "tank" | "centrifugal_pump" | "reciprocating_pump" | "metering_pump"
  | "reactor" | "heat_exchanger" | "vessel" | "column" | "compressor"
  | "blower" | "filter" | "dryer" | "mixer" | "conveyor";

export type ValveSubtype =
  | "gate_valve" | "globe_valve" | "ball_valve" | "butterfly_valve"
  | "check_valve" | "control_valve" | "safety_valve"
  | "three_way_valve" | "needle_valve";

export type InstrumentSubtype =
  | "transmitter" | "indicator" | "indicator_controller"
  | "alarm_high" | "alarm_low" | "switch" | "element" | "relay";

export type FittingSubtype =
  | "reducer" | "tee" | "blind_flange" | "expansion_joint";

// ---------------------------------------------------------------------------
// Sub-types (신규)
// ---------------------------------------------------------------------------

export interface Nozzle {
  id: string;
  label: string;
  side: "left" | "right" | "top" | "bottom";
  offset: number;
}

export interface EdgeProperties {
  size?: string;
  spec?: string;
  insulation?: string;
  fluid?: string;
  temperature?: string;
  pressure?: string;
}

// ---------------------------------------------------------------------------
// Core interfaces (기존 구조 유지 + 신규 필드 추가)
// ---------------------------------------------------------------------------

export interface CanonicalMetadata {
  area?: string;
  revision?: string;
  [key: string]: any;
}

export interface CanonicalNode {
  id: string;
  type: string;
  subtype: string;
  tag?: string;                         // optional 유지
  name?: string;
  position: { x: number; y: number };
  properties?: Record<string, any>;
  nozzles?: Nozzle[];                   // 신규
  [key: string]: any;
}

export interface CanonicalEdge {
  id: string;
  from_node: string;
  to_node: string;
  type?: EdgeType;
  from_port?: string;                   // 신규
  to_port?: string;                     // 신규
  line_number?: string;                 // 신규
  properties?: EdgeProperties;          // 신규
  waypoints?: { x: number; y: number }[]; // 신규
  [key: string]: any;
}

export interface DiagramCanonical {
  canonical_schema_version: number;
  id?: string;
  name?: string;
  diagram_type?: "pfd" | "pid" | "bfd";
  project_id?: string;
  metadata?: CanonicalMetadata;
  nodes: CanonicalNode[];
  edges: CanonicalEdge[];
  signal_lines?: any[];                 // 기존 유지
}