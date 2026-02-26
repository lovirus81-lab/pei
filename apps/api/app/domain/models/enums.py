"""도메인 열거형 — 프레임워크 의존성 없음"""
from __future__ import annotations

from enum import Enum


class NodeType(str, Enum):
    EQUIPMENT = "equipment"
    VALVE = "valve"
    INSTRUMENT = "instrument"
    FITTING = "fitting"


class EdgeType(str, Enum):
    PROCESS = "process"
    UTILITY = "utility"
    SIGNAL_ELECTRICAL = "signal_electrical"
    SIGNAL_PNEUMATIC = "signal_pneumatic"
