from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.project import DiagramCanonical
from app.services import repair

router = APIRouter(
    prefix="/repair",
    tags=["repair"]
)

class RepairRequest(BaseModel):
    canonical_json: DiagramCanonical
    repairs: List[Dict[str, Any]]

@router.post("/", response_model=DiagramCanonical)
async def repair_diagram(request: RepairRequest):
    try:
        updated_canonical = repair.apply_repairs(request.canonical_json, request.repairs)
        return updated_canonical
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
