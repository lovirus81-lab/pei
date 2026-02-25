// layout/elk-layout-engine.ts — ELK 레이아웃 엔진 (layout 계층)
// 프론트엔드 클라이언트사이드에서 실행. 백엔드 /generate/layout API 대체.

import ELK from "elkjs/lib/elk.bundled.js";
import type { DiagramCanonical } from "../domain/types/diagram";
import { buildElkGraph, extractPositions } from "./elk-adapter";

// ELK 인스턴스 — 재사용 (생성 비용이 있음)
// elk.bundled.js는 UMD 번들. Vite가 pre-bundle하여 ESM default export로 래핑한다.
const elk = new ELK();

/**
 * DiagramCanonical을 받아 ELK 레이아웃 알고리즘을 적용한 후
 * 각 노드에 새 Position이 설정된 DiagramCanonical을 반환한다.
 *
 * 이 함수는 원본 다이어그램을 수정하지 않는다.
 * 레이아웃 실패 시 원본 다이어그램을 그대로 반환한다.
 */
export async function applyElkLayout(
  diagram: DiagramCanonical
): Promise<DiagramCanonical> {
  if (diagram.nodes.length === 0) return diagram;

  try {
    const elkGraph = buildElkGraph(diagram);
    const laidOut = await elk.layout(elkGraph);
    return extractPositions(diagram, laidOut);
  } catch (error) {
    console.error("[elk-layout-engine] Layout failed, using original positions:", error);
    return diagram;
  }
}
