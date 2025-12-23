from typing import Dict, List, Optional
from datetime import datetime, date
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# App-level OpenAPI metadata and tags
openapi_tags = [
    {"name": "Health", "description": "Service health and status endpoints."},
    {"name": "Tasks", "description": "CRUD operations for to-do tasks."},
    {"name": "Habits", "description": "CRUD operations and tracking for habits."},
]

app = FastAPI(
    title="Habit & To-Do Tracker API",
    description="Backend API providing endpoints for tasks and habits with basic in-memory storage. "
                "This is a starter implementation to unblock frontend integration.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, restrict origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores (replace with database in future iterations)
TASKS: Dict[str, dict] = {}
HABITS: Dict[str, dict] = {}

# Pydantic models
class Pagination(BaseModel):
    page: int = Field(1, description="Page number starting from 1")
    size: int = Field(20, description="Number of items per page")


class TaskBase(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Optional detailed description")
    due_date: Optional[date] = Field(None, description="Due date for the task")
    priority: Optional[int] = Field(3, description="Priority from 1 (high) to 5 (low)")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    completed: bool = Field(False, description="Completion status")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    description: Optional[str] = Field(None, description="Updated description")
    due_date: Optional[date] = Field(None, description="Updated due date")
    priority: Optional[int] = Field(None, description="Updated priority")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    completed: Optional[bool] = Field(None, description="Updated completion status")


class Task(TaskBase):
    id: str = Field(..., description="Unique task identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class HabitBase(BaseModel):
    name: str = Field(..., description="Name of the habit")
    description: Optional[str] = Field(None, description="Optional description")
    frequency: str = Field("daily", description="Frequency definition (daily/weekly/custom)")
    target: Optional[int] = Field(None, description="Target number for quantitative habits")
    unit: Optional[str] = Field(None, description="Unit for quantitative habits (e.g., reps, minutes)")
    tags: List[str] = Field(default_factory=list, description="Tags for organization")


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    frequency: Optional[str] = Field(None, description="Updated frequency")
    target: Optional[int] = Field(None, description="Updated target")
    unit: Optional[str] = Field(None, description="Updated unit")
    tags: Optional[List[str]] = Field(None, description="Updated tags")


class Habit(HabitBase):
    id: str = Field(..., description="Unique habit identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check")
def health_check():
    """Service liveness probe endpoint returning a simple payload."""
    return {"message": "Healthy", "service": "Habit & To-Do Tracker API"}


# TASK ROUTES
# PUBLIC_INTERFACE
@app.get(
    "/tasks",
    response_model=List[Task],
    tags=["Tasks"],
    summary="List tasks",
    description="Retrieve a paginated list of tasks with optional tag and completion filters.",
)
def list_tasks(
    page: int = Query(1, ge=1, description="Page index starting from 1"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
):
    items = list(TASKS.values())
    if tag is not None:
        items = [t for t in items if tag in t.get("tags", [])]
    if completed is not None:
        items = [t for t in items if t.get("completed") is completed]

    start = (page - 1) * size
    end = start + size
    return [Task(**t) for t in items[start:end]]


# PUBLIC_INTERFACE
@app.post(
    "/tasks",
    response_model=Task,
    tags=["Tasks"],
    summary="Create task",
    description="Create a new task and return the created entity.",
)
def create_task(payload: TaskCreate):
    now = datetime.utcnow()
    task_id = str(uuid.uuid4())
    record = {
        "id": task_id,
        "title": payload.title,
        "description": payload.description,
        "due_date": payload.due_date,
        "priority": payload.priority if payload.priority is not None else 3,
        "tags": payload.tags or [],
        "completed": payload.completed,
        "created_at": now,
        "updated_at": now,
    }
    TASKS[task_id] = record
    return Task(**record)


# PUBLIC_INTERFACE
@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    summary="Get task by ID",
    description="Retrieve a task by its unique identifier.",
)
def get_task(task_id: str):
    record = TASKS.get(task_id)
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**record)


# PUBLIC_INTERFACE
@app.patch(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    summary="Update task",
    description="Apply partial updates to a task by ID.",
)
def update_task(task_id: str, payload: TaskUpdate):
    record = TASKS.get(task_id)
    if not record:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        record[k] = v
    record["updated_at"] = datetime.utcnow()
    TASKS[task_id] = record
    return Task(**record)


# PUBLIC_INTERFACE
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    tags=["Tasks"],
    summary="Delete task",
    description="Delete a task by its unique identifier.",
)
def delete_task(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    del TASKS[task_id]
    return


# HABIT ROUTES
# PUBLIC_INTERFACE
@app.get(
    "/habits",
    response_model=List[Habit],
    tags=["Habits"],
    summary="List habits",
    description="Retrieve all habits with basic pagination.",
)
def list_habits(
    page: int = Query(1, ge=1, description="Page index starting from 1"),
    size: int = Query(50, ge=1, le=200, description="Page size"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
):
    items = list(HABITS.values())
    if tag is not None:
        items = [h for h in items if tag in h.get("tags", [])]

    start = (page - 1) * size
    end = start + size
    return [Habit(**h) for h in items[start:end]]


# PUBLIC_INTERFACE
@app.post(
    "/habits",
    response_model=Habit,
    tags=["Habits"],
    summary="Create habit",
    description="Create a new habit and return the created entity.",
)
def create_habit(payload: HabitCreate):
    now = datetime.utcnow()
    habit_id = str(uuid.uuid4())
    record = {
        "id": habit_id,
        "name": payload.name,
        "description": payload.description,
        "frequency": payload.frequency,
        "target": payload.target,
        "unit": payload.unit,
        "tags": payload.tags or [],
        "created_at": now,
        "updated_at": now,
    }
    HABITS[habit_id] = record
    return Habit(**record)


# PUBLIC_INTERFACE
@app.get(
    "/habits/{habit_id}",
    response_model=Habit,
    tags=["Habits"],
    summary="Get habit by ID",
    description="Retrieve a habit by its unique identifier.",
)
def get_habit(habit_id: str):
    record = HABITS.get(habit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Habit not found")
    return Habit(**record)


# PUBLIC_INTERFACE
@app.patch(
    "/habits/{habit_id}",
    response_model=Habit,
    tags=["Habits"],
    summary="Update habit",
    description="Apply partial updates to a habit by ID.",
)
def update_habit(habit_id: str, payload: HabitUpdate):
    record = HABITS.get(habit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Habit not found")

    updates = payload.model_dump(exclude_unset=True)
    for k, v in updates.items():
        record[k] = v
    record["updated_at"] = datetime.utcnow()
    HABITS[habit_id] = record
    return Habit(**record)


# PUBLIC_INTERFACE
@app.delete(
    "/habits/{habit_id}",
    status_code=204,
    tags=["Habits"],
    summary="Delete habit",
    description="Delete a habit by its unique identifier.",
)
def delete_habit(habit_id: str):
    if habit_id not in HABITS:
        raise HTTPException(status_code=404, detail="Habit not found")
    del HABITS[habit_id]
    return
