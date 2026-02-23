from fastapi import APIRouter, HTTPException
from app.schemas.generator_models import (
    GenerateRequest, GenerateResponse,
    RepairRequest, RepairResponse,
    AiAssistRequest, AiAssistResponse,
    GenerateLayoutRequest, GenerateLayoutResponse
)
from app.services import generator, layout

router = APIRouter(
    prefix="/generate",
    tags=["generation"]
)

@router.post("/layout", response_model=GenerateLayoutResponse)
async def generate_layout_endpoint(req: GenerateLayoutRequest):
    try:
        updated_diagram = layout.apply_layout(req.diagram)
        return GenerateLayoutResponse(diagram=updated_diagram)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/template", response_model=GenerateResponse)
async def generate_template_endpoint(req: GenerateRequest):
    try:
        diagram = generator.generate_template(req.template_type)
        return GenerateResponse(
            diagram=diagram,
            template_type=req.template_type,
            node_count=len(diagram.nodes),
            edge_count=len(diagram.edges)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models

@router.post("/repair", response_model=RepairResponse)
async def auto_repair_endpoint(
    req: RepairRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(models.Ruleset).where(models.Ruleset.status == "active").order_by(models.Ruleset.created_at.desc())
    result = await db.execute(stmt)
    ruleset = result.scalars().first()
    rules = []
    if ruleset:
        stmt = select(models.Rule).where(
            models.Rule.ruleset_id == ruleset.id,
            models.Rule.kind == "validate",
            models.Rule.enabled == True
        )
        result = await db.execute(stmt)
        rules = result.scalars().all()

    diagram, repairs, remaining = generator.auto_repair(req.diagram, req.violations, rules)
    return RepairResponse(
        diagram=diagram,
        repairs=repairs,
        remaining_violations=remaining
    )

@router.post("/ai-assist", response_model=AiAssistResponse)
async def ai_assist_endpoint(req: AiAssistRequest):
    result = generator.ai_assist(req.diagram, req.request)
    return AiAssistResponse(**result)
