from typing import List, Optional, Any, Dict
from pydantic import BaseModel

from app.schemas.canonical import DiagramCanonical
from app.schemas.rules import Violation

class GenerateLayoutRequest(BaseModel):
    diagram: DiagramCanonical

class GenerateLayoutResponse(BaseModel):
    diagram: DiagramCanonical

class GenerateRequest(BaseModel):
    template_type: str

class GenerateResponse(BaseModel):
    diagram: DiagramCanonical
    template_type: str
    node_count: int
    edge_count: int

class RepairRequest(BaseModel):
    diagram: DiagramCanonical
    violations: List[Violation]

class RepairResponse(BaseModel):
    diagram: DiagramCanonical
    repairs: List[Dict[str, Any]]
    remaining_violations: List[Violation]

class AiAssistRequest(BaseModel):
    diagram: DiagramCanonical
    request: str

class AiAssistResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    auto_applicable: bool
    modified_diagram: Optional[DiagramCanonical] = None
