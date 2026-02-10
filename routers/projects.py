from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.db import get_db
from services import crud
from schemas import schemas
from models import models
from services.artic_client import get_artwork


router = APIRouter()


@router.post("/", response_model=schemas.ProjectOut, status_code=201)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):

    if len(payload.places) != len(set(payload.places)):
        raise HTTPException(status_code=409, detail="Duplicate places are not allowed")

    missing = []
    for external_id in payload.places:
        if not get_artwork(external_id):
            missing.append(external_id)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Artwork(s) not found in Art Institute API: {missing}",
        )

    try:
        project = models.Project(
            name=payload.name,
            description=payload.description,
            start_date=payload.start_date,
            completed=False,
        )
        db.add(project)
        db.flush()

        for external_id in payload.places:
            db.add(models.ProjectPlace(project_id=project.id, external_id=external_id))

        db.commit()
        db.refresh(project)
        return project

    except Exception:
        db.rollback()
        raise



@router.get("/", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return crud.list_projects(db)


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.start_date is not None:
        project.start_date = payload.start_date

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    visited = crud.project_has_visited_places(db, project_id)
    if visited:
        raise HTTPException(
            status_code=409,
            detail="Project cannot be deleted because it has visited places",
        )

    crud.delete_project(db, project)
