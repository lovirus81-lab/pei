from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.generator_models import (
    GenerateRequest, GenerateResponse,
    RepairRequest, RepairResponse,
    AiAssistRequest, AiAssistResponse,
)
from app.domain.services.template_service import generate_template
from app.domain.services.repair_service import auto_repair
from app.layout.layout_service import SlotLayoutService
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/generate",
    tags=["generation"]
)

# 슬롯 레이아웃 서비스 인스턴스 (싱글턴 — 상태 없음)
_layout_service = SlotLayoutService()


# NOTE: /generate/layout 엔드포인트가 제거되었습니다.
# 레이아웃은 프론트엔드에서 elkjs를 통해 클라이언트사이드로 처리됩니다.
# 백엔드 슬롯 레이아웃이 필요한 경우 repair 서비스에서 layout_engine으로 주입됩니다.


@router.post("/template", response_model=GenerateResponse)
async def generate_template_endpoint(req: GenerateRequest):
    """
    표준 P&ID 템플릿을 생성해 반환한다.
    위치 계산(레이아웃)은 포함되지 않음 — 프론트엔드가 elkjs로 처리한다.
    """
    try:
        diagram = generate_template(req.template_type)
        return GenerateResponse(
            diagram=diagram,
            template_type=req.template_type,
            node_count=len(diagram.nodes),
            edge_count=len(diagram.edges)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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

    diagram, repairs, remaining = await auto_repair(
        req.diagram, req.violations, rules, _layout_service
    )
    return RepairResponse(
        diagram=diagram,
        repairs=repairs,
        remaining_violations=remaining
    )


@router.post("/ai-assist", response_model=AiAssistResponse)
async def ai_assist_endpoint(req: AiAssistRequest):
    # AI assist는 향후 구현 예정
    return AiAssistResponse(
        suggestions=[
            {
                "description": f"AI perceived request: '{req.request}'. Suggesting insertion of Flow Transmitter.",
                "confidence": 0.85
            }
        ],
        auto_applicable=True,
        modified_diagram=None
    )
