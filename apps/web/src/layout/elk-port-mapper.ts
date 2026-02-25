// layout/elk-port-mapper.ts — Nozzle → ElkPort 변환 (layout 계층)

import type { Nozzle } from "../domain/types/geometry";

// elk.js 내장 타입을 사용
type ElkPort = {
  id: string;
  layoutOptions?: Record<string, string>;
};

const SIDE_MAP: Record<string, string> = {
  left: "WEST",
  right: "EAST",
  top: "NORTH",
  bottom: "SOUTH",
};

export function nozzleToElkPort(nozzle: Nozzle): ElkPort {
  return {
    id: nozzle.id,
    layoutOptions: {
      "elk.port.side": SIDE_MAP[nozzle.side] ?? "EAST",
    },
  };
}
