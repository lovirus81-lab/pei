// types/canonical.ts — 호환성 shim
// 새 위치: src/domain/types/diagram.ts
// 기존 import 경로를 유지하기 위한 re-export.

export type {
  NodeType,
  EdgeType,
  Position,
  Nozzle,
  EdgeProperties,
  CanonicalNode,
  CanonicalEdge,
  CanonicalMetadata,
  DiagramCanonical,
} from "../domain/types/diagram";

// 기존 코드 호환성을 위한 추가 타입들
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
