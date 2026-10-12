# GCP Production Deployment TODO

Status legend: `[ ]` todo, `[x]` done. Work top to bottom; phases 0-2 are code/repo work, 3+ is infra and pipeline.
Note: the Dockerfiles (backend/Dockerfile, frontend/Dockerfile) and docker-compose.yml were being handled by a separate parallel agent. Don't duplicate that work, just review it in Phase 1.

---

## Phase 0: Repo and secrets (do first)

- [ ] Create a dedicated git repo for this project. Currently the git root is `C:\Users\laksh` (home dir) with remote `L-Gupta/my-portfolio`, and no project files are tracked.
  - [ ] Never run `git add .` at the home-dir level (`.ssh/`, `.claude.json` etc. sit there untracked).
  - [ ] Create new GitHub repo, `git init` inside `ai-agent-interview-coach/`, confirm `.gitignore` covers `.env`, `venv/`, `*.db`, `uploads/`, `reports/`, `node_modules/`.
  - [ ] Check `backend/file/uploads/test_resume.pdf` and `backend/interview_coach.db` contain no real PII before committing anything.
- [ ] Rotate every key in `.env` (Gemini, Pinecone, OpenAI, JWT `SECRET_KEY`). Treat as compromised if they ever left this machine.
- [ ] Fill in `.env.example` with placeholder names only (empty values).
- [ ] `backend/core/config.py`: fail startup when `DEBUG=False` and `SECRET_KEY` / API keys are still the default placeholders (`"your-secret-key-change-in-production"`, `"your-gemini-api-key"`, ...).
- [ ] Remove unused settings (`REDIS_URL`, `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`) or wire them in.

## Phase 1: Blockers in current code

- [ ] **Public `/reports` mount**: `backend/main.py` serves `./reports` with no auth, and `config.py` always creates that dir. Interview audio/video lands there. Remove the mount; serve media via signed GCS URLs.
- [ ] **In-memory `active_sessions = {}`** (`backend/api/v1/interview.py`): breaks on restart / scale-out / scale-to-zero ("Session orchestrator not found").
  - [ ] Persist orchestrator state (use the unused `agent_memory` column, or Redis/Memorystore).
  - [ ] Stopgap only: `max-instances=1`.
- [ ] **Resume upload** (`backend/file/agentic_file_router.py`):
  - [ ] `/file/upload-resume` has no auth (imports `get_current_active_user` but never uses it); add `Depends(get_current_active_user)`.
  - [ ] Nothing creates a `Resume` DB row, so `/interview/start` always 404s ("Resume not found"). Create the row on upload (user_id, resume_id, filename, file_path, processed).
  - [ ] Files saved as `{user_supplied_resume_id}.pdf`, so users can overwrite each other; generate server-side UUIDs.
  - [ ] Enforce `MAX_UPLOAD_SIZE` (defined, never used); validate content type / magic bytes, not just extension.
  - [ ] Add auth + ownership checks to `resume-status`, `reprocess-resume`, `pipeline-logs` too (anyone guessing a `resume_id` can read status or re-run the Gemini/Pinecone pipeline).
- [ ] **Frontend/backend endpoint mismatch**:
  - [ ] `frontend/src/api.js` calls `/interview/{id}/submit-answer`, `/report`, `/end`. Backend only has `/start`, `/{id}/question`, `/{id}/answer`, `/{id}/status`. Implement report/end endpoints and align names.
  - [ ] `SummaryComponent.jsx` and `components/interview/exit.js` hardcode `http://127.0.0.1:8000/interview/...` (non-existent paths); route through `api.js` / `BASE_URL`.
- [ ] **Local paths hardcoded and inconsistent**: `file/uploads`, `end/reports`, `./reports` used directly; `settings.UPLOAD_DIR` / `REPORTS_DIR` unused.
  - [ ] Create one storage module backed by GCS (local-disk implementation for dev).
  - [ ] Move resume files, parsed text/chunks, and interview audio/video there.

## Phase 2: Backend hardening

**Database**
- [ ] Set up Alembic (in requirements, not configured); create initial migration; stop relying on `Base.metadata.create_all` at startup.
- [ ] Connection pooling settings; `echo=False` in prod.
- [ ] `/health` should run a real `SELECT 1` (currently reports "connected" unconditionally); add separate liveness/readiness.
- [ ] Cloud SQL URL form: `postgresql+psycopg2://user:pw@/db?host=/cloudsql/PROJECT:REGION:INSTANCE`.

**Auth**
- [ ] Add `/auth/refresh` endpoint (refresh token is issued but never usable).
- [ ] Login/register rate limiting (slowapi and/or Cloud Armor); password policy.
- [ ] Decide on email verification (`is_verified` unused).
- [ ] Consider httpOnly cookies instead of `localStorage` tokens (needs same-site via load balancer).
- [ ] Replace `datetime.utcnow()` with timezone-aware UTC.

**Request handling**
- [ ] Sync TensorFlow / MediaPipe / librosa / Gemini calls run inside `async def` handlers and block the event loop: use `run_in_threadpool`, or move to a worker (Cloud Tasks / Pub/Sub).
- [ ] Cloud Run HTTP/1 request body cap is 32 MiB: interview video will exceed it. Do direct browser-to-GCS upload via signed URLs.
- [ ] Set Cloud Run request timeout appropriately (15 min+) for analysis.

**Ops**
- [ ] Replace `print()` with structured JSON logging (Cloud Logging severity).
- [ ] Replace `@app.on_event("startup")` with lifespan handler.
- [ ] CORS: restrict `ALLOWED_ORIGINS` to exact frontend origin(s); tighten methods/headers.
- [ ] Security headers middleware; disable `/docs` and `/openapi.json` in prod (or protect).
- [ ] Optional: switch Gemini from API key to Vertex AI + service account.
- [ ] Pin dependency versions in `backend/requirements.txt` (everything is `>=`); produce a lockfile.

**Dockerfile (backend)**
- [ ] Add non-root user.
- [ ] Port: container hardcodes 1600; either set Cloud Run container port to 1600 or use `$PORT`.
- [ ] Multi-stage build to shrink image (TF-CPU + OpenCV + MediaPipe + librosa = multi-GB).
- [ ] Plan for 2 CPU / 4-8 GiB memory, `--cpu-boost`, min-instances 1.

**Tests**
- [ ] Real pytest suite (current `test_integration.py`, `test_file_module.py`, `test_file_functionality.py` are ad-hoc scripts); Postgres service container in CI.

## Phase 3: Frontend

- [ ] `REACT_APP_API_URL` is baked in at build time: use runtime `config.js` injected at container start (one image for staging + prod), or per-env builds.
- [ ] `package-lock.json` is out of sync so `npm ci` fails; regenerate (CI needs `npm ci`).
- [ ] nginx: listen on 8080, use `nginx-unprivileged`, add gzip, cache headers for hashed assets, security headers. Do NOT set a `Permissions-Policy` that blocks camera/microphone (`getUserMedia` is required).
- [ ] CRA / react-scripts 5.0.1 is deprecated; fine to ship, consider Vite later.
- [ ] Same-origin via load balancer (`/api/*` -> backend) so CORS/cookies are simple.

## Phase 4: GCP infrastructure (Terraform, state in GCS bucket)

- [ ] Separate staging and prod (ideally separate GCP projects).
- [ ] Artifact Registry (images).
- [ ] Cloud Run: backend (min-instances 1, concurrency ~4-8, timeout 15 min+, 2 CPU / 4-8 GiB) and frontend (nginx). Alternative for frontend: Firebase Hosting / GCS + CDN.
- [ ] Cloud SQL Postgres 16: private IP, automated backups, PITR, HA in prod. Test a restore.
- [ ] GCS buckets: uniform access, no public access, lifecycle rules for retention.
- [ ] Secret Manager for all secrets, mounted as env vars.
- [ ] Global HTTPS load balancer + managed cert + Cloud DNS; route `/api/*` -> backend, `/` -> frontend; restrict backend ingress to the LB.
- [ ] Cloud Armor (WAF + rate limiting).
- [ ] One service account per service, least privilege.
- [ ] Optional: Memorystore Redis (session state), Cloud Tasks / Pub/Sub (async analysis worker).
- [ ] Observability: Cloud Logging, Monitoring uptime checks + alerts, Error Reporting, budget alerts.
- [ ] Enable audit logs.
- [ ] Pinecone is external SaaS and stays outside GCP. If everything must be on GCP, swap to pgvector (Cloud SQL) or Vertex AI Vector Search; only `backend/file/file_pinecone.py` needs replacing (`upsert_embeddings`, `query_resume`, `delete_resume_vectors`).

## Phase 5: Branching and CI/CD

- [ ] Protect `main` (PR + review + passing checks); `main` auto-deploys to staging.
- [ ] Prod trigger: version tags `v*` with manual-approval GitHub Environment (recommended), or a `production` branch.
- [ ] GCP auth from GitHub Actions via Workload Identity Federation (no JSON keys). Alternative: Cloud Build triggers.
- [ ] Pipeline stages:
  - [ ] Lint / type-check (ruff, eslint)
  - [ ] Tests (pytest with Postgres service container)
  - [ ] Dependency audit (pip-audit, npm audit)
  - [ ] Secret scan (gitleaks)
  - [ ] Docker build + Trivy scan + push to Artifact Registry (tag = git SHA)
  - [ ] Alembic migration as a Cloud Run Job
  - [ ] Deploy `--no-traffic`, smoke test, gradual traffic shift
  - [ ] Rollback = route traffic to previous revision
- [ ] Dependabot or Renovate.

## Phase 6: Security and privacy checklist (pre-launch)

- [ ] HTTPS only + HSTS.
- [ ] Cloud SQL not publicly reachable; no public buckets.
- [ ] Backend not directly invokable (LB-only ingress).
- [ ] Upload size caps + content validation.
- [ ] Run `/security-review` on the full diff.
- [ ] Load test staging.
- [ ] Privacy: app records video/audio and runs face/emotion analysis (biometric data under GDPR, Illinois BIPA, etc.). Need:
  - [ ] Consent screen
  - [ ] Privacy policy + terms
  - [ ] Retention/deletion policy enforced by GCS lifecycle rules
  - [ ] User data-deletion path
  - (Not legal advice; get it reviewed.)

## Suggested order

1. Phase 0 (repo, rotate secrets, `.env.example`)
2. Phase 1 blockers
3. Phase 2 Alembic + tests + config hardening
4. Terraform staging, deploy manually once
5. CI/CD against staging
6. Load + security testing, create prod, cut first tag
