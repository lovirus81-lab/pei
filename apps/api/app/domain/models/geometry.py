"""도메인 기하학 값 객체 — 프레임워크 의존성 없음"""
from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float
    y: float


class Nozzle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str                          # e.g., "inlet", "discharge", "drain"
    side: str                           # "left" | "right" | "top" | "bottom"
    offset: float = 0.5                 # 0.0~1.0, position along the side


class EdgeProperties(BaseModel):
    size: str | None = None             # e.g., '6"'
    spec: str | None = None             # e.g., "A1A"
    insulation: str | None = None
    fluid: str | None = None
    temperature: str | None = None
    pressure: str | None = None
