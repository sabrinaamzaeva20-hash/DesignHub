import os
from datetime import date, datetime
import httpx
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="DesignHub Backend")
DATABASE_URL = os.environ["DATABASE_URL"]
PRICING_URL = os.getenv("PRICING_URL", "http://web-service:8001")
CATEGORIES = {"Брендинг", "Соцсети", "Веб-дизайн", "Полиграфия"}
STATUSES = {"В работе", "На проверке", "Завершён"}

class ProjectInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    client: str = Field(min_length=2, max_length=160)
    category: str = "Брендинг"
    status: str = "В работе"
    deadline: date | None = None

class StatusInput(BaseModel):
    status: str

class EstimateInput(BaseModel):
    category: str
    quantity: int = Field(ge=1, le=1000)
    urgency: bool = False

def serialize(row):
    result = dict(row)
    for key in ("deadline", "created_at"):
        if isinstance(result.get(key), (date, datetime)):
            result[key] = result[key].isoformat()
    return result

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/projects")
def get_projects():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    return [serialize(row) for row in rows]

@app.post("/api/projects", status_code=201)
def add_project(item: ProjectInput):
    if item.category not in CATEGORIES or item.status not in STATUSES:
        raise HTTPException(status_code=422, detail="Недопустимая категория или статус")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        row = conn.execute(
            """INSERT INTO projects (name, client, category, status, deadline)
               VALUES (%s, %s, %s, %s, %s) RETURNING *""",
            (item.name, item.client, item.category, item.status, item.deadline)
        ).fetchone()
    return serialize(row)

@app.patch("/api/projects/{project_id}")
def change_status(project_id: int, item: StatusInput):
    if item.status not in STATUSES:
        raise HTTPException(status_code=422, detail="Недопустимый статус")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        row = conn.execute(
            "UPDATE projects SET status=%s WHERE id=%s RETURNING *",
            (item.status, project_id)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return serialize(row)

@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: int):
    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute("DELETE FROM projects WHERE id=%s RETURNING id", (project_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Проект не найден")

@app.post("/api/estimate")
async def estimate(item: EstimateInput):
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(f"{PRICING_URL}/calculate", json=item.model_dump())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Сервис расчёта временно недоступен") from exc
