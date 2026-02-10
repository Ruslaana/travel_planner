from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectCreate(ProjectBase):
    places: List[int] = Field(min_length=1, max_length=10)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None


class ProjectOut(ProjectBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True


class PlaceCreate(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None


class PlaceOut(BaseModel):
    id: int
    external_id: int
    project_id: int
    notes: Optional[str] = None
    visited: bool

    class Config:
        orm_mode = True
