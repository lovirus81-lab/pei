# schemas/canonical.py — 호환성 shim
# 새 위치: app/domain/models/{enums,geometry,diagram}.py
# 기존 코드의 import 경로를 유지하기 위한 re-export.

from app.domain.models.enums import NodeType, EdgeType          # noqa: F401
from app.domain.models.geometry import Position, Nozzle, EdgeProperties  # noqa: F401
from app.domain.models.diagram import CanonicalNode, CanonicalEdge, DiagramCanonical  # noqa: F401
