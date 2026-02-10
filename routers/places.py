from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.db import get_db
from services import crud
from services.artic_client import get_artwork
from schemas import schemas

router = APIRouter()


@router.post("/{project_id}/places", response_model=schemas.PlaceOut)
def add_place(project_id: int, payload: schemas.PlaceCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if crud.count_project_places(db, project_id) >= 10:
        raise HTTPException(status_code=409, detail="Maximum 10 places allowed")

    if crud.place_exists(db, project_id, payload.external_id):
        raise HTTPException(status_code=409, detail="Place already exists")

    artwork = get_artwork(payload.external_id)
    if not artwork:
        raise HTTPException(status_code=400, detail="Artwork not found")

    return crud.create_place(db, project_id, payload.external_id)


@router.get("/{project_id}/places", response_model=list[schemas.PlaceOut])
def list_places(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.list_places(db, project_id)



@router.get("/{project_id}/places/{place_id}", response_model=schemas.PlaceOut)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    place = crud.get_place(db, project_id, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.patch("/{project_id}/places/{place_id}", response_model=schemas.PlaceOut)
def update_place(project_id: int, place_id: int, payload: schemas.PlaceUpdate, db: Session = Depends(get_db)):

    place = crud.get_place(db, project_id, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    if payload.notes is not None:
        place.notes = payload.notes
    if payload.visited is not None:
        place.visited = payload.visited

    db.commit()
    db.refresh(place)

    crud.update_project_completion(db, project_id)

    return place
