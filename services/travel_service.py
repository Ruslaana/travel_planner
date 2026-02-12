from __future__ import annotations

import asyncio
from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import models
from services import crud
from services.artic_client import validate_artworks_exist_async


def _run_async(coro):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError(
        "Async event loop is running. Make the endpoint 'async def' and await the coroutine.")


class TravelService:
    def __init__(self, db: Session):
        self.db = db

    def create_project_with_places(
        self,
        name: str,
        description: Optional[str],
        start_date: Optional[date],
        places: list[int],
    ) -> models.Project:
        # validations
        if not places:
            raise HTTPException(
                status_code=422, detail="Project must contain 1–10 places")
        if len(places) > 10:
            raise HTTPException(
                status_code=422, detail="Project must contain 1–10 places")
        if len(places) != len(set(places)):
            raise HTTPException(
                status_code=409, detail="Duplicate places are not allowed")

        missing = _run_async(validate_artworks_exist_async(places))
        if missing:
            raise HTTPException(
                status_code=400, detail=f"Artwork(s) not found: {missing}")

        project = models.Project(
            name=name,
            description=description,
            start_date=start_date,
            completed=False,
        )
        try:
            with self.db.begin():
                self.db.add(project)
                self.db.flush()

                for external_id in places:
                    self.db.add(
                        models.ProjectPlace(
                            project_id=project.id,
                            external_id=external_id,
                            notes=None,
                            visited=False,
                        )
                    )

            self.db.refresh(project)
            return project
        except HTTPException:
            raise
        except Exception:
            self.db.rollback()
            raise

    def add_place(self, project_id: int, external_id: int) -> models.ProjectPlace:
        project = crud.get_project(self.db, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        if crud.count_project_places(self.db, project_id) >= 10:
            raise HTTPException(
                status_code=409, detail="Maximum 10 places allowed")

        if crud.place_exists(self.db, project_id, external_id):
            raise HTTPException(status_code=409, detail="Place already exists")

        missing = _run_async(validate_artworks_exist_async([external_id]))
        if missing:
            raise HTTPException(status_code=400, detail="Artwork not found")

        try:
            with self.db.begin():
                place = models.ProjectPlace(
                    project_id=project_id,
                    external_id=external_id,
                    notes=None,
                    visited=False,
                )
                self.db.add(place)

            self.db.refresh(place)
            return place
        except HTTPException:
            raise
        except Exception:
            self.db.rollback()
            raise

    def update_place(
        self,
        project_id: int,
        place_id: int,
        notes: str | None,
        visited: bool | None,
    ) -> models.ProjectPlace:
      place = crud.get_place(self.db, project_id, place_id)
      if not place:
        raise HTTPException(status_code=404, detail="Place not found")

      if notes is not None:
          place.notes = notes
      if visited is not None:
          place.visited = visited

      try:
        self.db.flush()
        crud.update_project_completion(self.db, project_id)

        self.db.commit()
        self.db.refresh(place)
        return place
      except Exception:
        self.db.rollback()
        raise
