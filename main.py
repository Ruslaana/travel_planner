from fastapi import FastAPI
from services.db import engine, Base

from models import models

from routers import projects, places

app = FastAPI(title="Travel Planner")

Base.metadata.create_all(bind=engine)

app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(places.router, prefix="/projects", tags=["Places"])


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Travel Planner API running"}
