from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.db import get_db
from services.travel_service import TravelService
from schemas import schemas
from services import crud
from fastapi import HTTPException

router = APIRouter()


@router.post("/{project_id}/places", response_model=schemas.PlaceOut, status_code=201)
def add_place(project_id: int, payload: schemas.PlaceCreate, db: Session = Depends(get_db)):
    service = TravelService(db)
    return service.add_place(project_id, payload.external_id)


@router.patch("/{project_id}/places/{place_id}", response_model=schemas.PlaceOut)
def update_place(project_id: int, place_id: int, payload: schemas.PlaceUpdate, db: Session = Depends(get_db)):
    service = TravelService(db)
    return service.update_place(project_id, place_id, payload.notes, payload.visited)


@router.get("/{project_id}/places", response_model=list[schemas.PlaceOut])
def list_places(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.list_places(db, project_id)
