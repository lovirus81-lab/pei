from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter()

@router.get("/isa-codes", response_model=List[schemas.Rule])
async def get_isa_codes(db: AsyncSession = Depends(get_db)):
    # Fetch rules that are ISA lookups
    stmt = select(models.Rule).where(
        models.Rule.kind == 'lookup',
        models.Rule.code.like('LKP-ISA-%')
    )
    result = await db.execute(stmt)
    rules = result.scalars().all()
    return rules

@router.get("/equipment-classes", response_model=List[schemas.Rule])
async def get_equipment_classes(db: AsyncSession = Depends(get_db)):
    # Fetch rules that are PIP lookups
    stmt = select(models.Rule).where(
        models.Rule.kind == 'lookup',
        models.Rule.code.like('LKP-PIP-%')
    )
    result = await db.execute(stmt)
    rules = result.scalars().all()
    return rules
