from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel

from app import database, models
from app.schemas.canonical import DiagramCanonical
from app.schemas.rules import ValidationReport
from app.services.validator import validate as validator_validate

router = APIRouter(
    prefix="/validate",
    tags=["validation"]
)

class ValidateRequestPayload(BaseModel):
    diagram: DiagramCanonical
    ruleset_id: Optional[str] = None

@router.get("/debug")
async def debug_validation_rules(db: AsyncSession = Depends(database.get_db)):
    stmt = select(models.Ruleset).where(models.Ruleset.status == "active").order_by(models.Ruleset.created_at.desc())
    result = await db.execute(stmt)
    ruleset = result.scalars().first()
    if not ruleset:
        return {"error": "No active ruleset found"}
        
    stmt = select(models.Rule).where(
        models.Rule.ruleset_id == ruleset.id,
        models.Rule.kind == "validate",
        models.Rule.enabled == True
    )
    result = await db.execute(stmt)
    rules = result.scalars().all()
    
    debug_info = []
    
    for rule in rules:
        condition = rule.condition_json
        if isinstance(condition, str):
            import json
            try:
                condition = json.loads(condition)
            except:
                condition = {}
                
        match_type = condition.get("match", "unknown")
        
        # Determine actual check keys
        checks = list(condition.get("check", {}).keys()) if "check" in condition else []
        if not checks and match_type == "node":
            # Direct check keys from condition (e.g. has_field, has_property)
            for k in ["has_field", "has_property", "tag_matches_pattern", "downstream_node", "upstream_node", "has_at_least_one_edge", "connected_node", "connected_node_with_label", "nozzle_with_label", "has_bypass", "has_utility_connection", "straight_pipe_upstream"]:
                if k in condition: checks.append(k)
        
        debug_info.append({
            "code": rule.code,
            "name": rule.name_ko,
            "match": match_type,
            "checks": checks,
            "condition": condition
        })
        
    return {
        "active_rules_count": len(rules),
        "rules": debug_info
    }


@router.post("", response_model=ValidationReport)
async def validate_diagram(
    req: ValidateRequestPayload,
    db: AsyncSession = Depends(database.get_db)
):
    # 1. ruleset_id가 없으면 DB에서 status="active" ruleset 조회
    if req.ruleset_id:
        stmt = select(models.Ruleset).where(models.Ruleset.id == req.ruleset_id)
        result = await db.execute(stmt)
        ruleset = result.scalar_one_or_none()
        if not ruleset:
            raise HTTPException(status_code=404, detail="Ruleset not found")
    else:
        stmt = select(models.Ruleset).where(models.Ruleset.status == "active").order_by(models.Ruleset.created_at.desc())
        result = await db.execute(stmt)
        ruleset = result.scalars().first()
        if not ruleset:
            raise HTTPException(status_code=404, detail="No active ruleset found")

    # 2. 해당 ruleset의 rules를 DB에서 로드 (kind="validate", enabled=True)
    stmt = select(models.Rule).where(
        models.Rule.ruleset_id == ruleset.id,
        models.Rule.kind == "validate",
        models.Rule.enabled == True
    )
    result = await db.execute(stmt)
    rules = result.scalars().all()

    # 3. validator.validate(canonical, rules) 호출
    report = validator_validate(req.diagram, rules)

    # 4. runs 테이블에 결과 저장
    # diagram_id가 없으면 runs 저장 생략 (canonical 쪽에 id 속성이 있으면 그 id를 사용)
    diagram_id = req.diagram.id
    if diagram_id:
        # Get diagram version
        diagram_stmt = select(models.Diagram).where(models.Diagram.id == diagram_id)
        diagram_result = await db.execute(diagram_stmt)
        diagram_model = diagram_result.scalar_one_or_none()
        
        # diagram_model이 있으면 DB 저장
        if diagram_model:
            diagram_version = diagram_model.version
            
            run = models.Run(
                diagram_id=diagram_id,
                diagram_version=diagram_version,
                ruleset_id=ruleset.id,
                ruleset_hash=ruleset.hash,
                result_json=report.model_dump(),
                passed=report.passed,
                error_count=report.error_count,
                warning_count=report.warning_count
            )
            db.add(run)
            await db.commit()
    
    # 5. ValidationReport 반환
    return report
