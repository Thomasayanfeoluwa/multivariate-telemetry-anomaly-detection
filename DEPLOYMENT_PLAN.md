# SWaT Monitoring Prototype — Deployment Plan

This document describes the next phase after Notebook 13's historical-replay feasibility test. Notebook 13 produced a **GO for building the application prototype**, not for production or live-plant deployment. This document is a plan; the application has not been implemented or deployed.

### Chosen deployment services

- **Model API:** Modal, running the FastAPI service and the frozen TCN inference code. Start with CPU; use a GPU only if Notebook 13 measurements show it is needed.
- **Frontend:** Vercel, serving the existing Vite/React single-page app. The frontend calls the Modal API; it does not run the model.
- **Database:** Neon PostgreSQL, accessed only by the backend for replay reports, alert episodes, and notification delivery records.
- **Notifications:** a small project-owned backend `HookNotifier` sends webhook notifications on run lifecycle changes and new alert episodes. It is not a separate notification platform or a browser-side secret.

Vercel is selected over Netlify because this is a static Vite/React app and Vercel supports that build and Git-based preview deployments directly. Netlify could also host it; there is no model-serving advantage to either frontend host. Modal is the model/API host, not Vercel.

## Current repository state

- Notebooks 01–12 contain the completed offline study. Notebook 13 is complete; its seven saved feasibility tests passed.
- Notebook 13 reproduced frozen scores across 181,031 sequences with max absolute difference `5.215e-08` and zero alert-flag disagreements. Stateful replay on the tested slices also had zero flag disagreements.
- Event results matched the recorded reference: 28/36 scenarios detected, 8 missed, 73 validation false-alarm periods; median delay was 0 seconds among detected scenarios only, p90 22.8 seconds, maximum 1,489 seconds.
- On the tested Windows CPU, single-sequence inference median was 2.64 ms against the dataset's 1 Hz cadence. This is model-only timing, not measured FastAPI/Modal response latency.
- Test G rejected all malformed fixtures and accepted the control input. G2 was rejected safely but its diagnostic misclassified an unexpected feature as an ordering problem; correct this before exposing validation through FastAPI.
- Notebook 13 justifies proceeding to a local, historical-replay application prototype. HTTP serving, deployed Modal performance, concurrent sessions, and real-plant behavior remain untested.
- The selected model artifacts exist locally under `nb08_artifacts/`: the TCN checkpoint, scaler, training metadata, and `frozen_thresholds.json`. The selected threshold in that file is `0.003906734725460411`. An identical copy of the TCN training folder also exists under `models/tcn_preliminary/`; treat the NB08 artifacts as the selection record and do not package both copies.
- The `frontend/` directory now contains a Vite/React/TypeScript starter and notification/database placeholders; it is not yet the SWaT dashboard. Its `App.tsx` is still template content.
- The current `backend/Dockerfile`, root `docker-compose.yml`, root and frontend `.env.example` files, three files in `configs/`, and files under `src/` and `tests/` are empty placeholders.
- `database/migrations/001_initial_schema.sql` exists but is empty. There is no configured PostgreSQL database or deployed database service.
- The frontend has empty `useRunNotifier.ts`, `NotificationHost.tsx`, and `App.test.tsx` placeholders. Its package manifest and lockfile have been reconciled, and the unused database-client placeholder/dependency has been removed. Frontend test scripts and packages can be added when implementation begins.
- The selected database is Neon, so the browser must use the backend API for all database access; do not connect the browser directly to Neon.
- Existing `backend/api`, `backend/data`, `backend/detection`, `backend/evaluation`, `backend/monitoring`, and `backend/utils` folders duplicate the intended root `src/` layout. Keep `src/` as the one Python implementation tree; use `backend/` only for Modal deployment entrypoint, Dockerfile, and runtime dependencies.
- Raw SWaT data and generated model artifacts must stay outside the source image and must not be committed unless dataset terms and artifact-sharing permissions have been checked.

## Recommended build order

1. **Carry forward Notebook 13's one validation fix.** Report unexpected/missing feature names separately from a correct feature set in the wrong order. Preserve the tested policy: exact feature order, exact window shape, finite numeric values, and strictly increasing timestamps; reject invalid data rather than silently imputing or reordering it.
2. **Implement and test the API locally first.** Reuse Notebook 13's frozen inference behavior. Keep per-run sequence buffers isolated, test reset/boundary handling and concurrent requests, and verify API scores against the notebook within a documented tolerance. Do not expose retraining, threshold-tuning, or plant-control endpoints.
3. **Measure the HTTP path.** Test serialization, validation, response time, and full replay duration locally. The Notebook 13 2.64 ms figure is model-only on its Windows CPU; it does not establish Modal or end-to-end latency. Use the measurements to decide whether replay can be synchronous or needs a Modal background job.
4. **Add Neon persistence and notifications.** Store run status, compact reports, alert episodes, and delivery state. Implement `HookNotifier` for run start/completion/failure and new alert episodes, with deduplication and bounded retries. Do not notify once per anomalous sample.
5. **Build the Vercel-hosted React interface.** Present replay progress, score/telemetry context, event outcomes, alert episodes, and limitations. Alerts remain advisory model outputs, never confirmed attacks or process failures.
6. **Integrate locally with Docker Compose.** Run the API and frontend together against synthetic fixtures and a test database. Keep secrets and restricted data out of the image and repository.
7. **Deploy in stages.** Deploy FastAPI/model inference to Modal and Neon-backed persistence after local tests pass; measure the deployed HTTP path. Then deploy the static React frontend to Vercel with only the public API URL configured. Allow only expected Vercel origins in API CORS.
8. **Release checks.** Run unit, API, parity, persistence, notification, frontend, and deployment smoke tests. Publish/share only after confirming SWaT data and model-artifact permissions.

The recommendation is **GO for building and validating a portfolio prototype**. It is **not** a GO for a production system: this evidence comes from in-process, single-machine replay; HTTP, concurrency, hosted infrastructure, dataset permissions, human response, and real-plant performance have not been demonstrated.

## Target repository structure

The layout below is the intended shape after implementation. Keep the research notebooks, reports, and artifacts in their existing locations; do not duplicate model files just to fit this tree.

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml                 # backend tests, frontend checks, image builds
├── backend/
│   ├── modal_app.py               # Modal image, FastAPI ASGI entrypoint
│   ├── Dockerfile                 # local Compose image; keep dependencies aligned
│   └── requirements.txt           # pinned API/inference runtime dependencies
├── configs/
│   ├── project.yaml               # research/project settings, if needed
│   ├── evaluation.yaml            # offline evaluation settings, if needed
│   └── robustness.yaml            # notebook robustness settings, if needed
├── data/
│   ├── raw/                       # local, permitted input data; never in image/Git
│   └── processed/                 # generated data; never in image/Git
├── frontend/                      # existing Vite + React + TypeScript scaffold
│   ├── vercel.json                # SPA fallback only if client-side routes need it
│   ├── package.json
│   ├── package-lock.json
│   └── src/
│       ├── App.tsx
│       ├── api/apiClient.ts
│       ├── components/
│       │   ├── AlertEpisodeList.tsx
│       │   ├── NotificationHost.tsx
│       │   ├── ReplayControls.tsx
│       │   ├── RunSummary.tsx
│       │   └── ScoreTimeline.tsx
│       ├── hooks/useRunNotifier.ts
│       ├── pages/Dashboard.tsx
│       ├── test/setup.ts
│       ├── types/api.ts
│       └── types/notifications.ts
├── models/                        # existing research artifacts; not copied into image
├── notebooks/                     # 01–12 unchanged; 13 is feasibility work
├── reports/
├── src/                           # single Python implementation tree
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
│   ├── notifications/
│   │   └── hook_notifier.py       # run and alert-episode webhook notifications
│   └── storage/
│       └── postgres_repository.py # Neon access, backend only
├── database/                      # existing migration placeholder
│   └── migrations/
│       └── 001_initial_schema.sql # replay_runs, alert_episodes, notification_deliveries
├── tests/
│   ├── conftest.py
│   ├── fixtures/                  # small synthetic, non-restricted input
│   ├── test_api.py
│   ├── test_data_validation.py
│   ├── test_detectors.py
│   ├── test_evaluation.py
│   ├── test_event_detection.py
│   └── test_monitoring.py
├── .env.example
├── .dockerignore
├── docker-compose.yml
├── DEPLOYMENT_PLAN.md
└── README.md
```

`src/` is the single Python implementation location; do not implement a second copy under `backend/`. The existing frontend is a Vite starter, so retain its package and TypeScript setup and replace the starter UI as frontend work begins. The named application files are planned targets, not a claim that they are implemented. Existing empty duplicate backend subfolders need not be populated; no folder cleanup is required to start the next phase.

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
- `POST /api/v1/replays` — create a replay for an allowlisted dataset and time range; return a run ID.
- `GET /api/v1/replays/{run_id}` — retrieve status and the saved report.
- `GET /api/v1/replays/{run_id}/alerts` — retrieve alert episodes for the dashboard.

Use Pydantic request/response schemas. Configure CORS for the Vercel production domain and chosen preview domain only; CORS is not authentication. Never accept arbitrary filesystem paths or raw-data uploads from a public browser. Apply replay size, duration, and concurrency limits. Do not expose a live process-control endpoint.

## Frontend responsibilities

Use React with TypeScript and a small set of components:

- Replay start/stop/status and selected time range.
- Telemetry and anomaly-score timelines with timestamps, units, and a visible frozen threshold.
- Alert episode list with start/end time, score, and the measurements that were unusual.
- Summary of replay duration, event coverage, detection delay, and false-alarm episodes when offline evaluation results are available.
- Clear status text that an alert means “unusual model score for review,” not “confirmed attack” or “equipment failure.”

Use one API client module and typed response definitions. The browser calls FastAPI and never connects directly to Neon. Keep `VITE_API_BASE_URL` public; do not put database URLs, webhook URLs, or Modal secrets in Vite variables. During an active replay, poll the run status at a modest interval for in-app progress/notifications; the backend `HookNotifier` sends outbound webhook alerts. Do not add global state management until ordinary component state proves insufficient.

The current Vite starter is scaffolding, not a designed monitoring UI. Keep the existing Vite/React/TypeScript setup; later replace the template screen, add the dashboard components and API client, and configure component tests. There is no need to create a separate frontend backend or connect the browser to the database.

## PostgreSQL decision: Neon

Use **Neon PostgreSQL** for run reports and alert history. The browser does not need a database SDK: all reads and writes go through FastAPI, which connects to Neon using its pooled connection URL.

Store only information needed to review model runs:

- `replay_runs`: run ID/status/timestamps, model version and artifact hash, dataset ID/hash and evaluated time range, aggregate detection/evaluation metrics, inference duration, and a compact report JSON.
- `alert_episodes`: run ID, start/end timestamps, peak score, frozen threshold, and selected feature-deviation context.
- `notification_deliveries`: run/event ID, destination label, status, attempt count, and last delivery time for deduplication and retry visibility.

Do **not** store raw SWaT rows or every per-timestamp score in PostgreSQL for the first version. Return score traces from the replay response for the active dashboard; retain compact reports and alert episodes for run history. If later requirements need full traces, measure volume first and decide whether to store a downsampled trace or a permitted output artifact.

Keep the database credential only in Modal Secrets. Use a pooled Neon connection string for the running service and short transactions; run versioned SQL migrations from `database/migrations/` once per deployment, not on every container startup. The frontend must use the FastAPI API, never a Postgres URL or public database key.

## Experiment records

Notebook 13 evaluates a frozen model; it does not train or compare new model experiments. No separate experiment-tracking service is needed. Record replay configuration, score-parity results, latency, event metrics, and limitations in Notebook 13's outputs/reports; save application replay reports and alert episodes in Neon. Revisit experiment tracking only if future work resumes model training or requires repeated experiment comparisons.

## HookNotifier and notification behavior

`HookNotifier` is a small project-owned backend component that posts a concise JSON notification to a configured webhook. The receiving destination (for example, a chosen chat or incident channel) can be selected later; no notification vendor is needed in the model runtime.

Send an event immediately when a replay starts, completes, or fails, and when a **new alert episode opens**. Include run ID, model version, timestamp, anomaly score, threshold, and a dashboard link where available. Do not send one message for every anomalous time-series row: adjacent threshold crossings belong to one episode, and per-row messages would overwhelm recipients. Save delivery status and deduplicate by run/event ID; retry temporary failures with bounded backoff.

Store the webhook URL in a Modal Secret, never in the frontend or Git. The UI's notification host shows active-run progress by polling the run API; outbound webhooks are server-to-server. Test webhook delivery with a mocked receiver in CI. Never include raw sensor payloads or sensitive dataset contents in notifications.

## Configuration and secrets

- The existing `configs/project.yaml`, `evaluation.yaml`, and `robustness.yaml` are empty research placeholders. Their intended roles are project/run settings, offline evaluation protocol, and robustness experiments. They are not application configuration and should not be repurposed for deployment.
- Do not create configuration files just to hold values already defined by the frozen artifact metadata. Read the selected threshold from `frozen_thresholds.json`; validate the checkpoint, scaler, feature order, and window against the Notebook 11 evidence.
- Use environment variables for non-secret runtime settings (Modal model-volume path, allowlisted dataset ID, Vercel API base URL, log level, and bounded replay limits). `.env.example` documents safe local variable names/defaults; actual `.env` files are ignored.
- Store `NEON_DATABASE_URL` and `HOOK_NOTIFIER_WEBHOOK_URL` as Modal Secrets. Never put secrets into `VITE_*` variables because they are embedded in browser JavaScript.
- If a future runtime setting genuinely needs a checked-in default, add one small application config file with comments and a single source of truth.

## Hosting and Docker

- **Production frontend — Vercel:** connect the repository and set the project root to `frontend/`; build with `npm ci` and `npm run build`, output `dist`. Set only the public `VITE_API_BASE_URL` to the Modal FastAPI URL. Add an SPA fallback only if client-side routes are introduced. Vercel preview builds make UI changes reviewable before release.
- **Production model/API — Modal:** define a Modal ASGI app that serves FastAPI and loads the selected model once per container. Package only runtime dependencies and the verified model bundle; mount artifacts read-only through Modal storage rather than copying notebooks or data into the image. Start on CPU. Modal can scale containers down when idle; account for a cold start on the first request and keep a warm container only if measured demo responsiveness justifies its cost.
- **Long replay handling:** Notebook 13 measures typical duration first. If the replay fits within a bounded HTTP request, return normally; otherwise submit a background Modal function, persist run status in Neon, return the run ID immediately, and let the UI poll. Do not add a queue service for this.
- **Local Docker:** root `docker-compose.yml` is for development/integration only. It can run a local FastAPI container and a static frontend server with the same Neon development branch or a local test database. Keep production routing as Vercel → Modal → Neon; do not imply Compose is the deployed production stack.
- **Modal image/Dockerfile:** use `backend/Dockerfile` or a Modal image definition, not two independent dependency lists. Exclude `.git`, virtual environments (including `cats/`), notebooks, raw data, ZIP archives, generated artifacts, caches, and local `.env` files from build context. Mount the authorized model/data at runtime.
- **Data permission gate:** before uploading SWaT data or model files to Modal or exposing any sample publicly, confirm the applicable iTrust/data-copy terms permit that use. If not, keep replay local and deploy only a synthetic demo.
- **Local run:** document copy/setup commands only after the Dockerfile and Compose file are implemented and tested.

Do not add Kubernetes, Redis, Celery, a separate PostgreSQL server, or cloud infrastructure-as-code for the first portfolio version. Modal handles the model/API execution, Neon provides managed PostgreSQL, and Vercel serves the static UI.

## Test plan

Use small synthetic fixtures in automated tests so CI does not need SWaT files or large model artifacts.

### Backend tests

- **Unit:** schema and timestamp validation; feature ordering; missing/invalid values; window warm-up; preprocessing; deterministic score/threshold behavior; alert episode grouping; PostgreSQL repository if included.
- **Parity:** retain a small fixed input sequence that verifies the inference wrapper returns the same scores and flags as the Notebook 13 reference within a documented numeric tolerance. This is the key model-integration test.
- **API:** health and model metadata; valid replay; malformed request; insufficient sequence history; unsupported dataset/path; clear error responses.
- **Integration:** start FastAPI with a fake detector and synthetic fixture; verify replay records, Neon writes (using a test database or isolated schema), alert episode creation, notification deduplication, and retry behavior without SWaT data.
- **Data-backed manual check:** after the automated suite passes, run the frozen model against the permitted local replay data and compare with Notebook 13 evidence. This is not a substitute for automated tests and should not run in ordinary CI.
- **Deployment check:** after Modal deployment, test the real HTTP endpoint, cold/warm starts, response/error schemas, run isolation, and measured replay latency. Notebook 13 does not cover these.

### Frontend tests

- Unit/component tests for replay controls, loading/error states, charts receiving aligned timestamps, alert list, and model-alert wording.
- One end-to-end smoke test: load dashboard, submit replay, and verify a result/alert summary appears. Use a mocked API in CI; reserve a real-model check for local/manual verification.
- Notification UI tests: run started/completed/failed and new alert episode appear once; duplicate samples do not create duplicate notifications.
- Check keyboard access, readable labels/units, and non-color-only alert status.

### CI checks

For pull requests, run Python lint/type checks selected for the implementation, backend unit/API tests, frontend lint/type checks/component tests, frontend production build, and local Docker build. Use synthetic fixtures only; never require Modal credentials, Neon credentials, webhook URLs, or SWaT data in CI. Do not automatically deploy from pull requests. Vercel previews may be enabled for the frontend; production Modal deploys should be a deliberate release action.

## Portfolio release checks

Before calling the prototype complete:

1. Notebook 13 parity and chronological replay checks pass, with limitations recorded.
2. The Modal API loads the exact selected checkpoint/scaler/features/window/threshold and reports a safe model version.
3. Backend and frontend tests pass; the local Compose stack starts from a clean checkout when permitted artifacts/configuration are supplied.
4. The demo explains benchmark scope, SWaT release uncertainty, false-alarm trade-offs, and that alerts require human review.
5. Neon stores replay summaries, alert episodes, and notification status only; raw restricted data are not copied into it.
6. Modal and Vercel secrets/domains/CORS are configured without exposing credentials in the browser bundle.
7. No raw restricted data, personal paths, credentials, local database dumps, or virtual environments are in Git or container images.
8. Any model artifact shared publicly or uploaded to a third party has been checked against dataset terms and project permissions.
9. Describe the result as a historical-replay monitoring prototype. Do not claim production deployment, real-plant effectiveness, prevented incidents, measured operator savings, or financial return without evidence.

## Deliberately out of scope for the first version

- Live SWaT/plant connections, control commands, or automatic actions.
- Retraining or changing the selected TCN/threshold during deployment work.
- User accounts, role management, multi-tenant access, and internet-facing write access.
- Redis, Celery, Kubernetes, and microservices.
- Financial ROI or cost-saving estimates without real operational and cost records.
- A separate experiment-tracking service for the current frozen-model feasibility and serving work.

## Official platform references

- [Modal Web Functions and ASGI apps](https://modal.com/docs/guide/webhooks)
- [Deploying Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Neon connection pooling](https://neon.com/docs/connect/connection-pooling)
