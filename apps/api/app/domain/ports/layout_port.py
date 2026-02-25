"""레이아웃 엔진 포트 — 의존성 역전을 위한 추상 인터페이스"""
from __future__ import annotations

from typing import Protocol

from app.domain.models.diagram import DiagramCanonical


class ILayoutEngine(Protocol):
    def apply_layout(self, diagram: DiagramCanonical) -> DiagramCanonical:
        """
        DiagramCanonical을 받아 각 노드에 Position을 계산해 반환.
        순수 함수: 사이드 이펙트 없음, 입력 다이어그램을 직접 수정하지 않는다.
        """
        ...
