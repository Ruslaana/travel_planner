from sqlalchemy.orm import Session
from models import models


def create_project(db: Session, data: dict) -> models.Project:
    project = models.Project(**data)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> models.Project | None:
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def list_projects(db: Session) -> list[models.Project]:
    return db.query(models.Project).all()


def delete_project(db: Session, project: models.Project) -> None:
    db.delete(project)
    db.commit()


def project_has_visited_places(db: Session, project_id: int) -> bool:
    visited_place = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.project_id == project_id,
            models.ProjectPlace.visited == True  # noqa: E712
        )
        .first()
    )
    return visited_place is not None


def update_project_completion(db: Session, project_id: int) -> None:
    project = get_project(db, project_id)
    if not project:
        return

    has_unvisited = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.project_id == project_id,
            models.ProjectPlace.visited == False
        )
        .first()
    )
    project.completed = (has_unvisited is None)



def count_project_places(db: Session, project_id: int) -> int:
    return (
        db.query(models.ProjectPlace)
        .filter(models.ProjectPlace.project_id == project_id)
        .count()
    )


def place_exists(db: Session, project_id: int, external_id: int) -> bool:
    existing = (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.project_id == project_id,
            models.ProjectPlace.external_id == external_id
        )
        .first()
    )
    return existing is not None


def create_place(db: Session, project_id: int, external_id: int) -> models.ProjectPlace:
    place = models.ProjectPlace(
        project_id=project_id,
        external_id=external_id,
        notes=None,
        visited=False
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def list_places(db: Session, project_id: int) -> list[models.ProjectPlace]:
    return (
        db.query(models.ProjectPlace)
        .filter(models.ProjectPlace.project_id == project_id)
        .all()
    )


def get_place(db: Session, project_id: int, place_id: int) -> models.ProjectPlace | None:
    return (
        db.query(models.ProjectPlace)
        .filter(
            models.ProjectPlace.project_id == project_id,
            models.ProjectPlace.id == place_id
        )
        .first()
    )
