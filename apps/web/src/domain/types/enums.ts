// domain/types/enums.ts — 도메인 열거형 (ReactFlow import 없음)

export type NodeType = "equipment" | "valve" | "instrument" | "fitting";

export type EdgeType =
  | "process"
  | "utility"
  | "signal_electrical"
  | "signal_pneumatic";
