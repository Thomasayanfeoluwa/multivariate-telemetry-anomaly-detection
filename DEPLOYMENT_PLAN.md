# SWaT Monitoring Prototype — Deployment Plan

This document describes the proposed path from the completed 12-notebook study to a portfolio-ready historical-monitoring prototype. It is a plan, not a claim that the application has been built or deployed.

### Chosen deployment services

- **Model API:** Modal, running the FastAPI service and the frozen TCN inference code. Start with CPU; use a GPU only if Notebook 13 measurements show it is needed.
- **Frontend:** Vercel, serving the existing Vite/React single-page app. The frontend calls the Modal API; it does not run the model.
- **Database:** Neon PostgreSQL, accessed only by the backend for replay reports, alert episodes, and notification delivery records.
- **Notifications:** a small project-owned backend `HookNotifier` sends webhook notifications on run lifecycle changes and new alert episodes. It is not a separate notification platform or a browser-side secret.

Vercel is selected over Netlify because this is a static Vite/React app and Vercel supports that build and Git-based preview deployments directly. Netlify could also host it; there is no model-serving advantage to either frontend host. Modal is the model/API host, not Vercel.

## Current repository state

- Notebooks 01–12 contain the completed offline study. Notebook 13 is the planned feasibility check and has not been implemented.
- The selected model artifacts exist locally under `nb08_artifacts/`: the TCN checkpoint, scaler, training metadata, and `frozen_thresholds.json`. The selected threshold in that file is `0.003906734725460411`. An identical copy of the TCN training folder also exists under `models/tcn_preliminary/`; treat the NB08 artifacts as the selection record and do not package both copies.
- The `frontend/` directory now contains a Vite/React/TypeScript starter and notification/database placeholders; it is not yet the SWaT dashboard. Its `App.tsx` is still template content.
- The current `backend/Dockerfile`, root `docker-compose.yml`, root and frontend `.env.example` files, three files in `configs/`, and files under `src/` and `tests/` are empty placeholders.
- `database/migrations/001_initial_schema.sql` exists but is empty. There is no configured PostgreSQL database or deployed database service.
- The frontend has empty `useRunNotifier.ts`, `NotificationHost.tsx`, and `App.test.tsx` placeholders. Its package manifest and lockfile have been reconciled, and the unused database-client placeholder/dependency has been removed. Frontend test scripts and packages can be added when implementation begins.
- The selected database is Neon, so the browser must use the backend API for all database access; do not connect the browser directly to Neon.
- Existing `backend/api`, `backend/data`, `backend/detection`, `backend/evaluation`, `backend/monitoring`, and `backend/utils` folders duplicate the intended root `src/` layout. Keep `src/` as the one Python implementation tree; use `backend/` only for Modal deployment entrypoint, Dockerfile, and runtime dependencies.
- Raw SWaT data and generated model artifacts must stay outside the source image and must not be committed unless dataset terms and artifact-sharing permissions have been checked.

## Recommended build order

1. **Notebook 13 — feasibility first.** Replay the frozen TCN chronologically. Verify the exact checkpoint, scaler, 42-feature order, 30-step window, threshold, sequence warm-up and partition boundaries. Check score parity against the existing saved scoring procedure. Measure detected/missed scenarios, delay for matched events, false-alarm episodes per hour of normal operation, and inference time; compare with existing baselines only where alignment is valid. Keep labels out of inference; use them only for offline evaluation. Do not retrain or retune the model.
2. **Backend inference on Modal.** Extract the verified inference path into FastAPI and deploy it as a Modal ASGI web app. Load the frozen artifacts once per warm container. Validate input columns, order, timestamps, missing values, and sequence length. Do not expose training or threshold-tuning endpoints.
3. **Backend tests.** Confirm preprocessing and score parity, input rejection, alert grouping, and API behavior before building the UI.
4. **Notifications and persistence.** Store each replay and its report in Neon. Use `HookNotifier` to notify on run start, completion/failure, and each newly opened alert episode. Do not send a notification for every above-threshold sample; continuous samples form one alert episode and per-sample notifications would flood recipients.
5. **Frontend.** Build the React interface for historical replay and human review: replay controls, telemetry and score timelines, alert history, run reports, and visible notifications. Label detections as model alerts, not confirmed attacks, causes, or faults.
6. **Local Docker Compose.** Use Compose for local end-to-end development and checks only. Production hosting is Vercel (frontend) plus Modal (FastAPI/model) plus Neon (PostgreSQL).
7. **CI and portfolio release.** Run backend and frontend checks in GitHub Actions. Publish the portfolio demo only after checking dataset and model-artifact sharing terms.

If Notebook 13 reveals scoring or portability problems, fix and verify those before proceeding to the API. A successful replay supports an application-feasibility claim; it does not prove real-plant performance or operational benefit.

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

`src/` is the single Python implementation location; do not implement a second copy under `backend/`. The existing frontend is a Vite starter, so retain its package and TypeScript setup, then replace starter UI only after Notebook 13. The named application files are planned targets, not files to implement now. Existing empty duplicate backend subfolders need not be populated; do not delete or move them during this documentation-only step.

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
- **Parity:** a small fixed input sequence verifies the inference wrapper returns the same scores and flags as the Notebook 13 reference within a documented numeric tolerance. This is the key model-integration test.
- **API:** health and model metadata; valid replay; malformed request; insufficient sequence history; unsupported dataset/path; clear error responses.
- **Integration:** start FastAPI with a fake detector and synthetic fixture; verify replay records, Neon writes (using a test database or isolated schema), alert episode creation, notification deduplication, and retry behavior without SWaT data.
- **Data-backed manual check:** after the automated suite passes, run the frozen model against the permitted local replay data and compare with Notebook 13 evidence. This is not a substitute for automated tests and should not run in ordinary CI.

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
