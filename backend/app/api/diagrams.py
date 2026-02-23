from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid

from app import database, models
from app.schemas import project as schemas

router = APIRouter(
    tags=["diagrams"]
)

# --- Projects sub-resource ---

@router.post("/projects/{project_id}/diagrams", response_model=schemas.Diagram, status_code=status.HTTP_201_CREATED)
async def create_diagram(
    project_id: str,
    diagram_in: schemas.DiagramCreate,
    db: AsyncSession = Depends(database.get_db)
):
    # Check if project exists
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    schema_version = diagram_in.canonical_json.get("canonical_schema_version", 1)
    
    diagram = models.Diagram(
        project_id=project_id,
        name=diagram_in.name,
        diagram_type=diagram_in.diagram_type,
        canonical_json=diagram_in.canonical_json,
        canonical_schema_version=schema_version,
        version=1,
        status="draft"
    )
    db.add(diagram)
    await db.commit()
    await db.refresh(diagram)
    return diagram

@router.get("/projects/{project_id}/diagrams", response_model=List[schemas.Diagram])
async def read_project_diagrams(
    project_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Diagram).where(models.Diagram.project_id == project_id)
    result = await db.execute(stmt)
    diagrams = result.scalars().all()
    return diagrams

# --- Top-level Diagram resources ---

@router.get("/diagrams/{diagram_id}", response_model=schemas.Diagram)
async def read_diagram(
    diagram_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Diagram).where(models.Diagram.id == diagram_id)
    result = await db.execute(stmt)
    diagram = result.scalar_one_or_none()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    return diagram

@router.put("/diagrams/{diagram_id}", response_model=schemas.Diagram)
async def update_diagram(
    diagram_id: str,
    diagram_in: schemas.DiagramUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Diagram).where(models.Diagram.id == diagram_id)
    result = await db.execute(stmt)
    diagram = result.scalar_one_or_none()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")

    # Update fields if provided
    if diagram_in.name:
        diagram.name = diagram_in.name
    
    if diagram_in.canonical_json:
        diagram.canonical_json = diagram_in.canonical_json
        # Auto-increment version on full update
        diagram.version += 1
        
    await db.commit()
    await db.refresh(diagram)
    return diagram

@router.get("/diagrams/{diagram_id}/export")
async def export_diagram(
    diagram_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Diagram).where(models.Diagram.id == diagram_id)
    result = await db.execute(stmt)
    diagram = result.scalar_one_or_none()
    if not diagram:
        raise HTTPException(status_code=404, detail="Diagram not found")
    
    # Return JSON with proper headers for download
    return diagram.canonical_json
