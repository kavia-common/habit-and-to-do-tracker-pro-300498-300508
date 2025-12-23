# Habit & To-Do Tracker API (FastAPI)

This service provides REST endpoints for Tasks and Habits to support the Flutter frontend. Current implementation uses in-memory storage to unblock frontend integration.

How to run (development)
- Ensure Python 3.10+ is available.
- Install dependencies: `pip install -r requirements.txt`
- Start server (uvicorn): `uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload`
- API docs: http://localhost:3001/docs
- OpenAPI JSON: http://localhost:3001/openapi.json

Endpoints (starter)
- Health:
  - GET / — service liveness
- Tasks:
  - GET /tasks — list tasks (filters: tag, completed; pagination: page, size)
  - POST /tasks — create task
  - GET /tasks/{task_id} — get a task
  - PATCH /tasks/{task_id} — update a task
  - DELETE /tasks/{task_id} — delete a task
- Habits:
  - GET /habits — list habits (filter: tag; pagination: page, size)
  - POST /habits — create habit
  - GET /habits/{habit_id} — get a habit
  - PATCH /habits/{habit_id} — update a habit
  - DELETE /habits/{habit_id} — delete a habit

OpenAPI generation
- Regenerate `interfaces/openapi.json` via:
  - Run the server and download from `/openapi.json`, or
  - Execute: `python -m src.api.generate_openapi` (from backend_api root)

Notes
- Storage is in-memory; data resets on restart.
- For production, replace stores with a database (env-configured). Add models/repositories and service layers.
- Restrict CORS origins in production.
