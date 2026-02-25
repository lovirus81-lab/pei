// rendering/adapters/edge-styles.ts — 엣지 타입별 렌더링 스타일 (rendering 계층)
// to-reactflow.ts에서 분리. 렌더링 관심사만 담당.

import type { CSSProperties } from "react";
import type { EdgeType } from "../../domain/types/enums";

export const EDGE_STYLES: Record<EdgeType, CSSProperties & { strokeDasharray?: string }> = {
  process: { stroke: "#000", strokeWidth: 2 },
  utility: { stroke: "#000", strokeWidth: 1.5, strokeDasharray: "6 3" },
  signal_electrical: { stroke: "#000", strokeWidth: 1, strokeDasharray: "2 2" },
  signal_pneumatic: { stroke: "#000", strokeWidth: 1, strokeDasharray: "2 2" },
};
