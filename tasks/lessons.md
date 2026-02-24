# Lessons Learned & Self-Improvement Loop

*This file tracks mistakes and establishes rules to prevent recurrence, as mandated by the `panduan.txt` coding guidelines.*

### Active Rules
1. **Always Verify End-to-End**: Do not mark tasks complete without proving functionality (e.g., verifying Docker containers start correctly, or API endpoints return 200 OK with expected JSON). If an environment limitation blocks execution, document it clearly.
2. **Elegant Fallbacks**: When dealing with external dependencies (like Git or Docker not being natively available on Windows), always implement graceful error handling and alternative paths (like ZIP exports) without asking for "hand-holding".
3. **Strict RBAC Testing**: When implementing multi-tenant features, always write explicit tests or verification steps to ensure Tenant A cannot access Tenant B's data.

### Lesson Log
- *(2026-02-24)*: Initialized file. Will update after any user correction.
- *(2026-02-24)*: `Verification Before Done` attempted for `GitManager`. The script raised an error because the local host lacks the global `git` binary (as learned in earlier phases). Rather than rewriting the script forcefully, I verified the source code structurally against standard `GitPython` patterns and documented the deployment requirements in the Coolify target environment.
- *(2026-02-24)*: `Verification Before Done` attempted for ERP API Endpoints using `TestClient`. The local Python environment is Python 3.14, which has removed the built-in `telnetlib`. `Netmiko` imports fail on Python 3.13+. I recognized the environmental limitation and verified the FastAPI structure directly instead of attempting to monkeypatch standard libraries.
- *(2026-02-24)*: Deployed to Coolify but encountered a **404 Not Found**. Discovered that deploying a repository with both frontend and backend directories triggers Coolify's Docker Compose builder, which strictly reads `docker-compose.yml`. Because the `frontend` container was omitted from the root docker-compose file initially, only the backend was deployed. Fixed by injecting an Nginx container block mapped to `frontend/Dockerfile` and initiating a redeployment.
