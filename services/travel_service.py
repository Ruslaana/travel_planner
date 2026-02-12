from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from services import crud
from services.artic_client import get_artwork_cached, validate_artworks_exist
from models import models


class TravelService:
    def __init__(self, db: Session):
        self.db = db

    def create_project_with_places(self, name: str, description: str | None, start_date, places: list[int]) -> models.Project:
        if len(places) != len(set(places)):
            raise HTTPException(status_code=409, detail="Duplicate places are not allowed")
        if len(places) < 1 or len(places) > 10:
            raise HTTPException(status_code=422, detail="Project must contain 1–10 places")

        missing = validate_artworks_exist(places)
        if missing:
            raise HTTPException(status_code=400, detail=f"Artwork(s) not found: {missing}")

        try:
            project = models.Project(
                name=name,
                description=description,
                start_date=start_date,
                completed=False,
            )
            self.db.add(project)
            self.db.flush()

            for external_id in places:
                self.db.add(models.ProjectPlace(project_id=project.id, external_id=external_id))

            self.db.commit()
            self.db.refresh(project)
            return project
        except Exception:
            self.db.rollback()
            raise

    def add_place(self, project_id: int, external_id: int) -> models.ProjectPlace:
        project = crud.get_project(self.db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if crud.count_project_places(self.db, project_id) >= 10:
            raise HTTPException(status_code=409, detail="Maximum 10 places allowed")

        if crud.place_exists(self.db, project_id, external_id):
            raise HTTPException(status_code=409, detail="Place already exists")

        if not get_artwork_cached(external_id):
            raise HTTPException(status_code=400, detail="Artwork not found")

        place = crud.create_place(self.db, project_id, external_id)
        return place

    def update_place(self, project_id: int, place_id: int, notes: str | None, visited: bool | None) -> models.ProjectPlace:
        place = crud.get_place(self.db, project_id, place_id)
        if not place:
            raise HTTPException(status_code=404, detail="Place not found")

        if notes is not None:
            place.notes = notes
        if visited is not None:
            place.visited = visited

        self.db.commit()
        self.db.refresh(place)

        crud.update_project_completion(self.db, project_id)
        return place
