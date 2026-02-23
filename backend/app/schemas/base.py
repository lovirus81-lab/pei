from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class RuleBase(BaseModel):
    code: str
    category: str
    kind: str
    scope: str
    severity: Optional[str] = None
    name_ko: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    condition_json: Optional[Any] = None
    action_json: Optional[Any] = None
    message_template: Optional[str] = None
    reference: Optional[str] = None
    layer: str
    priority: int = 100
    is_overridable: bool = False
    enabled: bool = True

class RuleCreate(RuleBase):
    pass

class Rule(RuleBase):
    id: str
    ruleset_id: str

    class Config:
        from_attributes = True

class ReferenceItem(BaseModel):
    code: str
    name: str # name_ko or generic name
    description: Optional[str] = None
    meta: Optional[Any] = None # Extra fields like 'letter', 'position'
