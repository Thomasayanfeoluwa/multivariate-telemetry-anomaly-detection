# SWaT Monitoring Prototype — Deployment Plan

This document describes the proposed path from the completed 12-notebook study to a portfolio-ready historical-monitoring prototype. It is a plan, not a claim that the application has been built or deployed.

## Current repository state

- Notebooks 01–12 contain the completed offline study. Notebook 13 is the planned feasibility check and has not been implemented.
- The selected model artifacts exist locally under `nb08_artifacts/`: the TCN checkpoint, scaler, training metadata, and `frozen_thresholds.json`. The selected threshold in that file is `0.003906734725460411`. An identical copy of the TCN training folder also exists under `models/tcn_preliminary/`; treat the NB08 artifacts as the selection record and do not package both copies.
- The current `backend/Dockerfile`, root `docker-compose.yml`, `.env.example`, three files in `configs/`, and files under `src/` and `tests/` are empty placeholders.
- There is no frontend directory and no database file or database service.
- Raw SWaT data and generated model artifacts must stay outside the source image and must not be committed unless dataset terms and artifact-sharing permissions have been checked.

## Recommended build order

1. **Notebook 13 — feasibility first.** Replay the frozen TCN chronologically. Verify the exact checkpoint, scaler, 42-feature order, 30-step window, threshold, sequence warm-up and partition boundaries. Check score parity against the existing saved scoring procedure. Measure event coverage and delay, false-alarm episodes, and inference time. Keep labels out of inference; use them only for offline evaluation. Do not retrain or retune the model.
2. **Backend inference.** Extract the verified inference path into a small Python service. Load the frozen artifacts once at startup. Validate input columns, order, timestamps, missing values, and sequence length. Do not expose training or threshold-tuning endpoints.
3. **Backend tests.** Confirm preprocessing and score parity, input rejection, alert grouping, and API behavior before building the UI.
4. **Frontend.** Build a React interface for historical replay and human review: replay controls, telemetry and score timelines, alert history, and a run summary. Label detections as model alerts, not confirmed attacks, causes, or faults.
5. **Persistence, if retaining history is desired.** Use SQLite for replay-run summaries and alert episodes. Do not put raw SWaT rows or the entire score stream in the database for the first version.
6. **Docker Compose.** Run the API and static frontend as two services. Mount permitted data and frozen artifacts read-only; persist only the SQLite file.
7. **CI and portfolio release.** Run backend and frontend checks and build both images in GitHub Actions. Publish a portfolio demo only after checking dataset and model-artifact sharing terms. Choose a hosting provider later, based on the replay's measured CPU, memory, storage, and runtime.

If Notebook 13 reveals scoring or portability problems, fix and verify those before proceeding to the API. A successful replay supports an application-feasibility claim; it does not prove real-plant performance or operational benefit.

## Target repository structure

The layout below is the intended shape after implementation. Keep the research notebooks, reports, and artifacts in their existing locations; do not duplicate model files just to fit this tree.

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # backend tests, frontend checks, image builds
├── backend/
│   ├── Dockerfile
│   └── requirements.txt           # small, pinned runtime dependencies only
├── configs/
│   ├── project.yaml               # research/project settings, if needed
│   ├── evaluation.yaml            # offline evaluation settings, if needed
│   └── robustness.yaml            # notebook robustness settings, if needed
├── data/
│   ├── raw/                       # local, permitted input data; never in image/Git
│   └── processed/                 # generated data; never in image/Git
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf                 # static site and same-origin /api proxy
│   ├── package.json
│   ├── package-lock.json
│   └── src/
│       ├── api/client.ts
│       ├── components/
│       ├── pages/Dashboard.tsx
│       └── types/
├── models/                        # existing research artifacts; not copied into image
├── notebooks/                     # 01–12 unchanged; 13 is feasibility work
├── reports/
├── src/                           # one Python source tree; do not duplicate in backend/app
│   ├── __init__.py
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── data/
│   │   └── validation.py
│   ├── detection/
│   │   └── tcn_inference.py
│   ├── evaluation/
│   │   └── replay_metrics.py
│   ├── monitoring/
│   │   └── logger.py
│   ├── replay/
│   │   └── runner.py
│   └── storage/
│       └── sqlite_repository.py   # only if persistent run history is included
├── tests/
│   ├── conftest.py
│   ├── fixtures/                  # small synthetic, non-restricted input
│   ├── test_api.py
│   ├── test_data_validation.py
│   ├── test_detectors.py
│   ├── test_evaluation.py
│   ├── test_event_detection.py
│   └── test_monitoring.py
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── DEPLOYMENT_PLAN.md
└── README.md
```

`src/` is the single Python implementation location. `backend/` contains the API container recipe and its runtime dependencies; do not create a second `backend/app/` implementation. The currently empty source/test files can be filled only when their stage begins. No source folders need to be deleted now.

## Backend responsibilities

The backend is a read-only inference and historical-replay service:

- Load the frozen TCN, scaler, ordered feature list, window size, and threshold once on startup. Notebook 13 must verify that this complete inference bundle is traceable and that the service reproduces the saved scores.
- Accept a replay request referring to a configured local dataset or an allowed sample. Do not accept arbitrary filesystem paths or upload raw industrial data through the public demo.
- Validate schema, timestamp ordering, numeric values, missing data, and minimum history before scoring. Return explicit validation errors rather than silently filling or reordering data.
- Score chronologically and return timestamped anomaly scores, threshold status, and relevant feature deviations. Keep labels out of inference.
- Keep event labels and evaluation metrics in offline replay evaluation, separate from inference responses.
- Begin with a simple replay request/response API. Add background jobs only if Notebook 13 shows replay duration exceeds practical request limits.

Small initial API surface:

- `GET /api/v1/health` — service readiness and model-loaded status; no sensitive paths.
- `GET /api/v1/model` — model name and public configuration summary (window, feature count, threshold version), not filesystem paths.
- `POST /api/v1/replays` — start a replay for an allowed dataset and time range.
- `GET /api/v1/replays/{run_id}` — retrieve the replay summary and alert episodes if persistence is enabled.

Use Pydantic request/response schemas. Keep CORS closed to cross-origin access when the frontend and API are served through the same Nginx origin. Do not expose a live process-control endpoint.

## Frontend responsibilities

Use React with TypeScript and a small set of components:

- Replay start/stop/status and selected time range.
- Telemetry and anomaly-score timelines with timestamps, units, and a visible frozen threshold.
- Alert episode list with start/end time, score, and the measurements that were unusual.
- Summary of replay duration, event coverage, detection delay, and false-alarm episodes when offline evaluation results are available.
- Clear status text that an alert means “unusual model score for review,” not “confirmed attack” or “equipment failure.”

Use one API client module and typed response definitions. Do not add global state management until ordinary component state proves insufficient. Do not add authentication to a local single-user demo; if the service is exposed publicly with user-specific data or write access, security requirements must be revisited first.

## Database decision

No database currently exists in the repository, and a separate database server is not needed for historical replay.

For a portfolio dashboard that should retain replay history across restarts, **SQLite is the smallest reasonable option**. Store only replay-run metadata, aggregate evaluation results, and alert episodes. Keep the database file in a Docker volume or ignored local runtime directory, never in Git. Do not add PostgreSQL, Redis, or a database container for this single-user prototype.

If persistent history is not needed, omit SQLite initially and return replay results directly; this is even simpler. The storage choice can be finalized after Notebook 13 establishes typical replay size and duration.

## Configuration and secrets

- The existing `configs/project.yaml`, `evaluation.yaml`, and `robustness.yaml` are empty research placeholders. Their intended roles are project/run settings, offline evaluation protocol, and robustness experiments. They are not application configuration and should not be repurposed for deployment.
- Do not create configuration files just to hold values already defined by the frozen artifact metadata. Read the selected threshold from `frozen_thresholds.json`; validate the checkpoint, scaler, feature order, and window against the Notebook 11 evidence.
- Use environment variables for runtime paths and ports (for example, model-artifact directory, allowed replay-data directory, and SQLite path). `.env.example` documents variable names and safe local defaults; actual `.env` files are ignored and must not contain committed secrets.
- If a future runtime setting genuinely needs a checked-in default, add one small application config file with comments and a single source of truth.

## Docker and local deployment

- **API image:** built from `backend/Dockerfile`, installs only pinned API/inference dependencies, runs as a non-root user, and starts Uvicorn. Do not install notebook, plotting, training, or drift-analysis packages in the runtime image unless the service actually needs them.
- **Frontend image:** builds the React assets and serves them with Nginx. Nginx serves the UI and proxies `/api/` to the API service, so the browser uses one origin.
- **Compose:** two services only (`api`, `web`). Expose the web port (default `8080`); keep the API port internal. Add health checks and start the web service after API health is available.
- **Mounts:** mount the frozen model artifacts and permitted replay data read-only. Keep the SQLite database, if used, in a named persistent volume.
- **Build context:** add `.dockerignore` before building. Exclude `.git`, virtual environments (including the local `cats/` environment), notebooks, raw data, ZIP archives, generated artifacts, caches, and local `.env` files. This prevents oversized images and accidental data disclosure.
- **Local run:** copy `.env.example` to `.env`, install Docker Desktop, check dataset/artifact availability, then use `docker compose up --build`. The exact command and required local files should be documented after the files exist and have been tested.

Do not add Kubernetes, a message queue, Redis, a separate PostgreSQL service, cloud infrastructure-as-code, or a production reverse-proxy stack for the first portfolio version. Reconsider a component only when a measured requirement needs it.

## Test plan

Use small synthetic fixtures in automated tests so CI does not need SWaT files or large model artifacts.

### Backend tests

- **Unit:** schema and timestamp validation; feature ordering; missing/invalid values; window warm-up; preprocessing; deterministic score/threshold behavior; alert episode grouping; SQLite repository if included.
- **Parity:** a small fixed input sequence verifies the inference wrapper returns the same scores and flags as the Notebook 13 reference within a documented numeric tolerance. This is the key model-integration test.
- **API:** health and model metadata; valid replay; malformed request; insufficient sequence history; unsupported dataset/path; clear error responses.
- **Integration:** start the API with a test checkpoint or injected fake detector and a synthetic fixture; verify an end-to-end replay and persistence behavior without depending on real data.
- **Data-backed manual check:** after the automated suite passes, run the frozen model against the permitted local replay data and compare with Notebook 13 evidence. This is not a substitute for automated tests and should not run in ordinary CI.

### Frontend tests

- Unit/component tests for replay controls, loading/error states, charts receiving aligned timestamps, alert list, and model-alert wording.
- One end-to-end smoke test: load dashboard, submit replay, and verify a result/alert summary appears. Use a mocked API in CI; reserve a real-model check for local/manual verification.
- Check keyboard access, readable labels/units, and non-color-only alert status.

### CI checks

For pull requests, run Python lint/type checks selected for the implementation, backend unit/API tests, frontend lint/type checks/component tests, frontend production build, and Docker image builds. Use synthetic fixtures only. Do not automatically deploy from pull requests. Add deployment automation only after a hosting target and secret-handling approach are explicitly chosen.

## Portfolio release checks

Before calling the prototype complete:

1. Notebook 13 parity and chronological replay checks pass, with limitations recorded.
2. The API loads the exact selected checkpoint/scaler/features/window/threshold and reports its version.
3. Backend and frontend tests pass; the Compose stack starts from a clean checkout when the required permitted artifacts are supplied.
4. The demo explains benchmark scope, SWaT release uncertainty, false-alarm trade-offs, and that alerts require human review.
5. No raw restricted data, personal paths, credentials, local databases, or virtual environments are in the Git image or repository.
6. Any model artifact shared publicly has been checked against the dataset terms and project permissions.
7. Describe the result as a historical-replay monitoring prototype. Do not claim production deployment, real-plant effectiveness, prevented incidents, measured operator savings, or financial return without evidence.

## Deliberately out of scope for the first version

- Live SWaT/plant connections, control commands, or automatic actions.
- Retraining or changing the selected TCN/threshold during deployment work.
- User accounts, role management, multi-tenant access, and internet-facing write access.
- PostgreSQL, Redis, Celery, Kubernetes, and microservices.
- Financial ROI or cost-saving estimates without real operational and cost records.
- A cloud-hosting provider choice before resource needs and artifact permissions are known.
