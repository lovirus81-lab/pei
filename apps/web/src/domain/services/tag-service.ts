// domain/services/tag-service.ts — 태그 생성 서비스 (ReactFlow import 없음)
// 기존: utils/tagGenerator.ts가 ReactFlow Node[]를 받았음
// 개선: CanonicalNode[]를 받아 도메인 계층 내에서 처리

import type { CanonicalNode } from "../types/diagram";
import { getTagPrefix } from "./tag-prefix-map";

/**
 * 도면 내 기존 노드의 태그를 스캔해 다음 순번 태그를 반환한다.
 * 순수 함수: 사이드 이펙트 없음.
 *
 * @param equipmentClass  노드의 subtype 또는 장비 클래스
 * @param existingNodes   현재 도면의 CanonicalNode 배열
 */
export function generateTag(
  equipmentClass: string,
  existingNodes: CanonicalNode[]
): string {
  const prefix = getTagPrefix(equipmentClass);
  let maxNumber = 100;

  for (const node of existingNodes) {
    const tag = node.tag;
    if (tag && tag.startsWith(`${prefix}-`)) {
      const numPart = tag.substring(prefix.length + 1);
      const num = parseInt(numPart, 10);
      if (!isNaN(num) && num > maxNumber) {
        maxNumber = num;
      }
    }
  }

  return `${prefix}-${maxNumber + 1}`;
}
