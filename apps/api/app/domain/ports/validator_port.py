"""검증기 포트 — 의존성 역전을 위한 추상 인터페이스"""
from __future__ import annotations

from typing import Any, Protocol

from app.domain.models.diagram import DiagramCanonical


class IValidator(Protocol):
    def validate(self, diagram: DiagramCanonical, rules: list[Any]) -> Any:
        """
        DiagramCanonical과 규칙 목록을 받아 ValidationReport를 반환.
        """
        ...
