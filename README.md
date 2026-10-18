# POLYPULSE — The Living Lesion Digital Twin

Greenfield research prototype for longitudinal tracking of synthetic endometrial-polyp observations. It is not a validated medical device, does not acquire ultrasound, diagnose disease, determine malignancy, or predict clinical outcomes. Procedural anatomy is illustrative, not patient-specific.

## Stack
React + TypeScript + Vite + React Three Fiber/Drei + Recharts; FastAPI + Pydantic + SQLAlchemy + Alembic; PostgreSQL primary, SQLite local demo.

## Run locally
Requirements: Node 20+, Python 3.11+.

Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate | macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs.

Frontend in a second terminal:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Set `VITE_API_BASE_URL=http://127.0.0.1:8000/api` as needed.

PostgreSQL: `docker compose up -d db`, then set `DATABASE_URL=postgresql+psycopg://polypulse:polypulse@localhost:5432/polypulse` in `backend/.env`. SQLite is the default local demo database.

## Commands
Frontend: `npm run dev`, `npm run build`, `npm run test`. Backend: `pytest`, `alembic upgrade head`, `python -m app.seed`.

## Workflow
Select fictional patient → start timed simulated scan → backend generates deterministic synthetic measurements → persist assessment/observation/measurement/telemetry/twin version in a transaction → inspect history and compare two records. A completed state is only shown after the API confirms the saved observation.

## API
`GET /api/health`; `GET /api/patients`; `GET /api/patients/{id}`; `GET /api/patients/{id}/observations`; `GET /api/observations/{id}`; `POST /api/assessments`; `GET /api/assessments/{id}`; `POST /api/assessments/{id}/process`; `POST /api/assessments/{id}/cancel`; `GET /api/patients/{id}/twin-state`; `GET /api/patients/{id}/comparisons?from_id=...&to_id=...`.

Timestamps are normalized to timezone-aware UTC, treating legacy naive values as UTC. Demo seed data is fictional and repeatable. For a safe reset, use only a dedicated demo database; delete the local SQLite file only after stopping the backend, then migrate and reseed.

## Limits
No real sensor integration, real ultrasound analysis, medical validation, patient-specific reconstruction, or clinical interpretation. Do not use this software for clinical decisions.
