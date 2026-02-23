from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.project import DiagramCanonical

class Violation(BaseModel):
    rule_code: str
    severity: str          # error / warning / info
    message: str
    node_id: str | None = None
    edge_id: str | None = None

class ValidationReport(BaseModel):
    passed: bool
    error_count: int
    warning_count: int
    violations: List[Violation]

class ValidateRequest(BaseModel):
    diagram_id: Optional[str] = None
    canonical_json: Optional[DiagramCanonical] = None
    ruleset_id: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

