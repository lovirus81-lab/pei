// stores/canvas-domain-store.ts — Canonical 도메인 상태 관리 (ReactFlow 타입 없음)
// canvas-store.ts (RF 렌더링 상태)와 분리된 순수 도메인 스토어.

import { create } from "zustand";
import type { DiagramCanonical, CanonicalNode } from "../domain/types/diagram";
import { generateTag } from "../domain/services/tag-service";
import { applyElkLayout } from "../layout/elk-layout-engine";

interface CanvasDomainState {
  /** 현재 편집 중인 도면의 Canonical 표현 */
  canonical: DiagramCanonical | null;

  /** Canonical 전체 교체 (DB 로드 등) */
  setCanonical: (diagram: DiagramCanonical) => void;

  /** 현재 canonical 반환 */
  getCanonical: () => DiagramCanonical | null;

  /**
   * 새 노드를 도메인 상태에 추가한다.
   * 태그는 도메인 서비스(tag-service.ts)에서 생성 — ReactFlow 타입 불사용.
   */
  addCanonicalNode: (
    node: Omit<CanonicalNode, "tag"> & { equipmentClass?: string }
  ) => void;

  /** 노드 및 연결 엣지 제거 */
  removeCanonicalNode: (nodeId: string) => void;

  /**
   * elkjs를 사용해 레이아웃을 계산하고 canonical을 업데이트한다.
   * 완료 후 업데이트된 DiagramCanonical을 반환.
   */
  applyElkLayout: () => Promise<DiagramCanonical | null>;

  /** 캔버스 초기화 */
  clearCanonical: () => void;
}

export const useCanvasDomainStore = create<CanvasDomainState>((set, get) => ({
  canonical: null,

  setCanonical: (diagram) => {
    set({ canonical: diagram });
  },

  getCanonical: () => get().canonical,

  addCanonicalNode: (node) => {
    const state = get();
    if (!state.canonical) return;

    // 태그 생성: CanonicalNode[] 기반 (ReactFlow Node[] 아님)
    const equipmentClass = node.equipmentClass ?? node.subtype;
    const tag = generateTag(equipmentClass, state.canonical.nodes);

    const newNode: CanonicalNode = {
      ...node,
      tag,
      properties: node.properties ?? {},
      nozzles: node.nozzles ?? [],
    };

    set({
      canonical: {
        ...state.canonical,
        nodes: [...state.canonical.nodes, newNode],
      },
    });
  },

  removeCanonicalNode: (nodeId) => {
    const state = get();
    if (!state.canonical) return;

    set({
      canonical: {
        ...state.canonical,
        nodes: state.canonical.nodes.filter((n) => n.id !== nodeId),
        edges: state.canonical.edges.filter(
          (e) => e.from_node !== nodeId && e.to_node !== nodeId
        ),
      },
    });
  },

  applyElkLayout: async () => {
    const state = get();
    if (!state.canonical) return null;

    const positioned = await applyElkLayout(state.canonical);
    set({ canonical: positioned });
    return positioned;
  },

  clearCanonical: () => {
    const state = get();
    if (!state.canonical) return;
    set({
      canonical: {
        ...state.canonical,
        nodes: [],
        edges: [],
      },
    });
  },
}));
