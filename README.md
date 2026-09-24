# eRTMAC-NWIS

Nearby Wells Intelligence System: an AI-assisted, location-aware decision-support prototype for drilling operations.http://localhost:5173

The system helps an engineer compare an active well with nearby historical wells, inspect historical drilling events, identify repeated depth intervals, view telemetry, and review model-estimated risks.

This is a decision-support prototype. It does not control drilling equipment, and model outputs are not guaranteed outcomes.

## Current MVP Status

Implemented and verified:

- FastAPI backend with SQLite and SQLAlchemy.
- Synthetic dataset generator with one active well and 35 historical wells.
- Synthetic depth-indexed drilling telemetry.
- Haversine nearby-well search.
- Formation, event, parameter, risk-zone, alert, and health APIs.
- Random Forest models for mud loss, stuck pipe, kick, and torque spike.
- Well-level ML splitting to reduce telemetry leakage.
- PDF upload and page-aware text extraction.
- In-memory lexical RAG search with metadata filtering.
- React/Vite dashboard with Leaflet map and Recharts telemetry charts.
- WebSocket endpoint for telemetry messages.
- Focused backend tests.

Prototype limitations:

- RAG is currently in-memory lexical retrieval, not a persistent Chroma/BM25/embedding pipeline.
- The WebSocket simulator sends telemetry but the dashboard does not yet consume live messages.
- JWT helpers exist, but login endpoints and protected routes are not complete.
- Docker Compose is currently only a placeholder.
- Alembic migration files are not configured; tables are created with SQLAlchemy metadata.
- Public scraping and source verification are only partially scaffolded.
- Synthetic data is not Oil India operational data.

## Repository Layout

```text
second/
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   `-- endpoints/       FastAPI route modules
|   |   |-- core/                Settings, database, storage, geospatial helpers
|   |   |-- extraction/          PDF and deterministic extraction logic
|   |   |-- ml/                  Training and prediction
|   |   |-- models/              SQLAlchemy models and enums
|   |   |-- rag/                 Prototype retrieval engine
|   |   |-- schemas/             Pydantic response/request models
|   |   |-- scraper/             Scraper scaffolding
|   |   `-- websocket/           Telemetry connection manager
|   |-- requirements.txt
|   |-- .env.example
|   `-- tests/
|-- data/
|   |-- nwis.db                  SQLite database created at runtime
|   |-- models/                  Trained model files
|   |-- raw/                     Uploaded and downloaded source files
|   `-- vectorstore/             Reserved for future persistent vectors
|-- frontend/
|   |-- src/pages/Dashboard.tsx
|   |-- src/components/Map.tsx
|   |-- src/components/ParameterCharts.tsx
|   |-- package.json
|   `-- vite.config.ts
`-- scripts/
		|-- generate_demo_data.py
		|-- train_models.py
		`-- simulate_realtime.py
```

## Prerequisites

Recommended local environment:

- Windows PowerShell.
- Python 3.11 or newer.
- Node.js 18 or newer.
- npm.
- Git.
- Optional: Tesseract OCR if scanned PDF extraction is required.

## First-Time Setup on Windows

From the repository root:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\second

python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r backend\requirements.txt

cd frontend
npm install
cd ..
```

If PowerShell blocks virtual-environment activation, run this once in an elevated or permitted shell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Configuration

Copy the example environment file:

```powershell
Copy-Item backend\.env.example backend\.env
```

Before using the project outside local development:

- Replace `JWT_SECRET` with a private random value.
- Do not commit `backend/.env`.
- Do not place private Oil India data in the repository.
- Mark all demo records as `SYNTHETIC`.

Important: the current database module creates and uses `data/nwis.db` from the repository root. `DATABASE_URL` is documented for future configuration but is not currently the controlling database path.

## Generate Demo Data

The generator clears existing demo wells, events, formations, users, and telemetry, then creates:

- `ACTIVE-001` as the active well.
- 35 historical wells around the synthetic Upper Assam location.
- Multiple formations per well.
- Historical mud-loss, stuck-pipe, kick, and torque-spike events.
- Depth-indexed synthetic drilling parameters.

Run:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\second
.\venv\Scripts\python.exe scripts\generate_demo_data.py
```

Do not run this command against a database containing data you need to preserve. It deletes existing demo records before reseeding.

## Train the Risk Models

Run after generating data:

```powershell
.\venv\Scripts\python.exe scripts\train_models.py
```

Models are written to `data/models/`:

```text
is_mud_loss_model.pkl
is_stuck_pipe_model.pkl
is_kick_model.pkl
is_torque_spike_model.pkl
```

The trainer uses a deterministic well-level split. Telemetry records from one well are kept in one split to reduce leakage between training and testing.

The metrics are for synthetic data only. Low recall or unstable metrics must be treated as a data-quality limitation, not as operational evidence.

## Start the Backend

Use a terminal from the repository root:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\second
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/v1/health -UseBasicParsing
```

## Start the Frontend

Use a second terminal:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\second\frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

If the browser shows an old Vite error, stop the existing frontend process with `Ctrl+C`, start one Vite process, and refresh with `Ctrl+F5`.

Build the frontend without starting a server:

```powershell
npm run build
```

The dashboard expects the backend at `http://127.0.0.1:8000/api/v1`.

## API Reference

All routes use the `/api/v1` prefix.

### Health

```text
GET /api/v1/health
```

### Wells

```text
GET /api/v1/wells
GET /api/v1/wells/{well_id}
GET /api/v1/wells/{well_id}/events
GET /api/v1/wells/{well_id}/formations
GET /api/v1/wells/{well_id}/parameters
GET /api/v1/wells/{well_id}/nearby?radius_km=10
GET /api/v1/wells/{well_id}/risk-zones?radius_km=10
GET /api/v1/wells/nearby?latitude=27.35&longitude=95.32&radius_km=10
```

Example:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/wells/ACTIVE-001/nearby?radius_km=10"
```

### Risk Prediction

```text
POST /api/v1/risk/predict
```

Example body:

```json
{
	"well_id": "ACTIVE-001",
	"depth": 2820,
	"rop": 10,
	"wob": 12,
	"rpm": 100,
	"torque": 20,
	"hook_load": 100,
	"standpipe_pressure": 120,
	"mud_weight": 1.15,
	"flow_rate": 1000,
	"ecd": 1.2
}
```

The response contains model-estimated probabilities and important model features. These values are not guaranteed probabilities.

### Alerts

```text
GET /api/v1/alerts
GET /api/v1/alerts?well_id=ACTIVE-001
POST /api/v1/alerts/evaluate
```

Example body:

```json
{
	"well_id": "ACTIVE-001",
	"current_depth": 2760,
	"radius_km": 10
}
```

### Documents

```text
POST /api/v1/documents/upload
```

The current upload route accepts PDF and CSV extensions. PDF text is extracted page by page and uploaded chunks are placed into the process-local RAG index.

### Search and Chat

```text
POST /api/v1/search
POST /api/v1/chat
```

Search example:

```json
{
	"query": "mud loss around 3000 meters",
	"well_id": "ACTIVE-001",
	"radius_km": 10
}
```

Chat example:

```json
{
	"question": "What drilling problems occurred near 3000 meters?",
	"well_id": "ACTIVE-001",
	"radius_km": 10
}
```

Chat evidence must include real indexed metadata. The API intentionally returns insufficient evidence instead of inventing missing well, depth, page, or document values.

### WebSocket

```text
WS /api/v1/ws/drilling/{well_id}
```

The current endpoint accepts JSON telemetry and broadcasts it to connected clients for the same well.

## Real-Time Demo

Start the backend first, then run the simulator from the repository root:

```powershell
.\venv\Scripts\python.exe scripts\simulate_realtime.py
```

The simulator connects to:

```text
ws://localhost:8000/api/v1/ws/drilling/ACTIVE-001
```

It sends synthetic depth, ROP, WOB, RPM, torque, mud weight, ECD, and flow-rate values while moving through the demo interval.

## Tests

Run all backend tests:

```powershell
cd C:\Users\DELL\OneDrive\Desktop\second
.\venv\Scripts\python.exe -m pytest -q
```

The current test suite covers the Haversine calculation, metadata filtering in the RAG engine, and the health endpoint. Expand it when adding new business logic.

## Database and Data Lineage

SQLite is stored at:

```text
data/nwis.db
```

Important SQLAlchemy models include:

- `Well`
- `Formation`
- `DrillingEvent`
- `DrillingParameter`
- `Document`
- `DocumentChunk`
- `RiskPrediction`
- `Alert`
- `DataSource`
- `User`

Every demo record should remain identifiable through `data_source_type`. Valid values are:

```text
REAL_PUBLIC
SYNTHETIC
USER_UPLOADED
```

Do not describe synthetic wells or events as real Oil India records.

## Team Development Workflow

1. Pull the latest branch.
2. Activate the virtual environment.
3. Install backend and frontend dependencies.
4. Generate demo data only when a reset is intended.
5. Start the backend and frontend in separate terminals.
6. Make one focused change at a time.
7. Add or update a test for backend behavior.
8. Run `pytest -q` and `npm run build` before opening a pull request.
9. Never commit `.env`, SQLite production data, model secrets, or private operational documents.

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Run Uvicorn from the repository root with `PYTHONPATH` set:

```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload
```

### Frontend shows a blank page

Confirm that `frontend/index.html` contains `<div id="root"></div>`, remove stale generated `.js` files under `frontend/src`, and restart Vite.

### Frontend cannot reach the API

Confirm both servers are running:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/v1/health -UseBasicParsing
Invoke-WebRequest http://localhost:5173 -UseBasicParsing
```

### Training reports no parameter data

Regenerate the demo database before training:

```powershell
python scripts\generate_demo_data.py
python scripts\train_models.py
```

### OCR returns no text

Text-layer PDFs work without Tesseract. Scanned PDFs require a working Tesseract installation available on `PATH`.

## Planned Work

The next implementation milestones are:

1. Add Alembic migrations and database lifecycle management.
2. Add authenticated login and role-based route protection.
3. Persist embeddings and implement Chroma/BM25 hybrid retrieval.
4. Apply well, radius, depth, and formation filters in search and chat.
5. Add complete source metadata and raw-file lineage tracking.
6. Connect WebSocket telemetry to the dashboard and alert evaluation.
7. Add DOCX ingestion and stronger document validation.
8. Implement safe public-source scraping with robots and rate-limit checks.
9. Add Docker services and persistent data volumes.
10. Expand unit, API, ingestion, ML, and WebSocket test coverage.

## Safety and Data Policy

This project is intended to support engineering review. It must not directly control drilling equipment. Historical evidence and model estimates must remain visually and technically distinguishable. Use only legitimate public sources or authorized user uploads, respect source terms and robots rules, and never bypass authentication, CAPTCHA, paywalls, or access controls.
#   s i h _ s e c o n d  
 