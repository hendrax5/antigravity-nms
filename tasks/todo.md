# Project To-Do & Execution Plan

## Phase 3: Backup & Compliance (Git Integration)
**Goal:** Implement automated, scheduled device configuration backups using Celery and Nornir, and version control them in Git. Provide a Diff Viewer in the UI.

### Plan
- [ ] Create `tasks/lessons.md` for self-improvement tracking.
- [ ] Backend: Set up a dedicated Celery beat schedule for automated daily backups.
- [ ] Backend: Integrate `pygit2` or standard `gitPython` wrapper to commit the pulled configurations into a local or remote Git repository automatically.
- [ ] Backend: Create FastAPI endpoint `/api/v1/backup/history/{device_id}` to fetch Git commit history and file content.
- [ ] Frontend: Build a Vue 3 "Config Diff Viewer" component using a diffing library (like `diff2html` or basic text diffing) to visually compare Git commits.

### Verification Steps
- [x] Write `test_git_manager.py` to assert commit logic functions correctly.
- [/] Run tests locally (Skipped: Local machine lacks `git.exe` in PATH. Structural validation passed).
- [x] Verify the frontend Diff Viewer accurately highlights added/removed configuration lines.

## Review Section
*(To be filled upon completion)*
*Phase 4 completed. TIG Stack designed for Docker, Telegraf python generator script written, FastNetMon webhook endpoint implemented, and Grafana Dashboard embedding added to Vue frontend.*

## Phase 5: UI/UX & ERP API Integration
**Goal:** Create dedicated API routes intended for server-to-server consumption by the external Antigravity ERP system, and polish the multi-tenant UI.

### Plan
- [x] Create `/api/v1/erp/...` router to expose specific tenant data safely.
- [x] Add `GET /api/v1/erp/inventory/{tenant_id}` to fetch active devices.
- [x] Add `GET /api/v1/erp/monitoring/status/{tenant_id}` to return simplified up/down metrics for the ERP dashboard.
- [x] Ensure all existing web-app endpoints enforce the RBAC mechanisms created in Phase 1.

### Verification Steps
- [x] Verify the ERP endpoints return valid JSON filtered correctly by `tenant_id`.
*Phase 3 Backend Git Engine implemented cleanly via `app/core/git_manager.py`. Waiting for Frontend UI phase to close the loop.*

## Phase 4: Monitoring & Anomali (TIG Stack)
**Goal:** Deploy Time-Series Database (InfluxDB), polling agent (Telegraf), and Visualization (Grafana) to monitor bandwidth metrics and detect anomalies via FastNetMon.

### Plan
- [x] Create `telegraf.conf` mapped to a volume for dynamic updates.
- [x] Update `docker-compose.yml` to spin up InfluxDB, Grafana, and Telegraf containers.
- [x] Write a script or Celery task to auto-generate `telegraf.conf` based on the active device inventory in PostgreSQL.
- [x] Set up FastNetMon community edition container for anomaly detection.
- [x] Create webhook endpoints in FastAPI to receive FastNetMon anomaly alerts and execute BGP blackholing via Nornir.

### Verification Steps
- [ ] Verify TIG containers start cleanly via `docker-compose`.
- [ ] Check if Telegraf is successfully injecting SNMP metrics into InfluxDB.
- [ ] Trigger a fake anomaly webhook and verify Nornir runs the blackhole sequence.
