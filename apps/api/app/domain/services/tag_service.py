"""태그 생성 서비스 — 순수 도메인 로직, I/O 없음"""
from __future__ import annotations

from app.domain.models.diagram import DiagramCanonical


def generate_sequential_tag(diagram: DiagramCanonical, prefix: str) -> str:
    """
    다이어그램 내 기존 태그를 스캔해 다음 순번 태그를 반환한다.
    예: prefix="P", 기존 P-101, P-102 → "P-103"

    순수 함수: 다이어그램을 수정하지 않음.
    """
    max_num = 100
    for node in diagram.nodes:
        if node.tag and node.tag.startswith(f"{prefix}-"):
            try:
                num = int(node.tag.replace(f"{prefix}-", ""))
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"{prefix}-{max_num + 1}"
