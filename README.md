# Travel Planner API

## Overview

Travel Planner API is a RESTful backend service that allows travellers to create travel projects, manage places they want to visit, attach notes, and track visit status.
The system integrates with the **Art Institute of Chicago API** to validate that places exist before adding them to projects.

The application is built using **FastAPI**, **SQLAlchemy**, and **SQLite**, and includes Docker support for easy local deployment.

---

## Features

* CRUD operations for travel projects
* Manage places inside projects (add, update, list, retrieve)
* Validation of places using the Art Institute of Chicago API
* Automatic project completion when all project places are marked as visited
* Prevent deletion of projects that contain visited places
* Limit of maximum **10 places per project**
* Docker support
* Postman collection included

---

## Tech Stack

* Python 3.10
* FastAPI
* SQLAlchemy
* SQLite
* HTTPX (third-party API integration)
* Docker

---

## Run locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start application

```bash
uvicorn main:app --reload
```

Application will be available at:

```
http://127.0.0.1:8000
```

Swagger documentation:

```
http://127.0.0.1:8000/docs
```

---

## Run with Docker

### Build image

```bash
docker build -t travel-planner .
```

### Run container

```bash
docker run -p 8000:8000 travel-planner
```

---

## API Endpoints

### Projects

* `POST /projects/` — create project (with optional places)
* `GET /projects/` — list projects
* `GET /projects/{project_id}` — get project
* `PATCH /projects/{project_id}` — update project
* `DELETE /projects/{project_id}` — delete project

### Places (nested)

* `POST /projects/{project_id}/places` — add place
* `GET /projects/{project_id}/places` — list project places
* `GET /projects/{project_id}/places/{place_id}` — get place
* `PATCH /projects/{project_id}/places/{place_id}` — update notes / mark visited

---

## Business Rules

* A project must contain **1–10 places**
* Duplicate places inside the same project are not allowed
* A place must exist in the Art Institute API before being added
* A project cannot be deleted if any place has been marked as visited
* When all places in a project are marked as visited, the project is automatically marked as **completed**

---

## Postman Collection

A ready-to-use Postman collection is included in the repository:

```
postman_collection.json
```

Import it into Postman and set:

```
base_url = http://127.0.0.1:8000
```

---

## Health Check

```
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

## Notes

This project was implemented as part of a Python backend engineering assessment and demonstrates REST API design, database modeling, validation logic, and third-party service integration.
