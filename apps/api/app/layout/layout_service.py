"""ILayoutEngine 구현체 — 슬롯 기반 레이아웃"""
from __future__ import annotations

from app.domain.models.diagram import DiagramCanonical
from app.domain.ports.layout_port import ILayoutEngine
from app.layout.slot_layout import apply_layout


class SlotLayoutService:
    """ILayoutEngine 프로토콜을 구현하는 슬롯 기반 레이아웃 서비스."""

    def apply_layout(self, diagram: DiagramCanonical) -> DiagramCanonical:
        return apply_layout(diagram)
