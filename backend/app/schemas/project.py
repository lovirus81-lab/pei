from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime

# Type aliases for repair/validation logic
CanonicalNode = Dict[str, Any]
CanonicalEdge = Dict[str, Any]

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Diagram Schemas
class CanonicalMetadata(BaseModel):
    area: Optional[str] = None
    revision: Optional[str] = None
    
class DiagramCanonical(BaseModel):
    canonical_schema_version: int = 1
    metadata: Optional[Dict[str, Any]] = {}
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    signal_lines: List[Dict[str, Any]] = []

class DiagramBase(BaseModel):
    name: str
    diagram_type: str = "PID"  # PFD, PID, etc.

class DiagramCreate(DiagramBase):
    canonical_json: Dict[str, Any]

class DiagramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    canonical_json: Optional[Dict[str, Any]] = None

class Diagram(DiagramBase):
    id: str
    project_id: str
    version: int
    status: str
    canonical_json: Dict[str, Any]
    canonical_schema_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
