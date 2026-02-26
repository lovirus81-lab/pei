// domain/types/geometry.ts — 도메인 기하학 값 객체 (ReactFlow import 없음)

export interface Position {
  x: number;
  y: number;
}

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
