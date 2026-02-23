from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app import database, models
from app.schemas import project as schemas

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: schemas.ProjectCreate,
    db: AsyncSession = Depends(database.get_db)
):
    project = models.Project(
        name=project_in.name,
        description=project_in.description
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@router.get("", response_model=List[schemas.Project])
async def read_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Project).offset(skip).limit(limit)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
async def read_project(
    project_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=schemas.Project)
async def update_project(
    project_id: str,
    project_in: schemas.ProjectCreate,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
        
    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(database.get_db)
):
    stmt = select(models.Project).where(models.Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Manual CASCADE for diagram relationships since ondelete isn't mapped
    delete_diagrams_stmt = select(models.Diagram).where(models.Diagram.project_id == project_id)
    diagrams_res = await db.execute(delete_diagrams_stmt)
    diagrams_to_delete = diagrams_res.scalars().all()
    
    for diagram in diagrams_to_delete:
        await db.delete(diagram)
        
    await db.delete(project)
    await db.commit()
    return None
