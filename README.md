# SentinelWatch
**Real-Time Security Log Monitoring & Brute-Force Detection System**

A defensive mini-SIEM. An external device (Kali VM) sends security events to a cloud REST API (FastAPI),
which stores them in PostgreSQL, detects brute-force behaviour, raises alerts, and shows everything on a React dashboard.

```
Kali VM (security_agent.py) --HTTPS--> FastAPI --> Detection Engine --> Alerts
                                          |                              |
                                          +-------> PostgreSQL <---------+
                                                        |
                                                 React Dashboard
```

> Lab use only. The agent sends synthetic events to YOUR OWN API. It never attacks anything.

## Detection rules (configurable via env vars)
| Failed logins from one IP in WINDOW_SECONDS (120) | Alert |
|---|---|
| >= 3 | MEDIUM (REPEATED_FAILURES) |
| >= 5 | HIGH (BRUTE_FORCE) |
| >= 10 | CRITICAL (BRUTE_FORCE) |
| one suspicious_login event | LOW |

## Project structure
```
backend/   FastAPI app (app/), tests/, requirements.txt, .env.example
frontend/  React + Vite dashboard
agent/     security_agent.py for Kali
docs/      api.md, testing.md
screenshots/  put your evidence here
```

# STEP-BY-STEP BUILD GUIDE

## Step 1 - Open the project (PowerShell)
Unzip `sentinelwatch.zip` to `Documents`, then:
```powershell
cd $HOME\Documents\sentinelwatch
code .
```

## Step 2 - Put it on GitHub (PowerShell in project folder)
1. On github.com click **New repository**, name it `sentinelwatch`, leave it EMPTY (no README), create.
2. Run:
```powershell
git init                      # make this folder a Git repository
git add .                     # stage all files (.gitignore keeps secrets out)
git status                    # confirm .env is NOT listed
git commit -m "Initial SentinelWatch project"
git branch -M main            # name the branch main
git remote add origin https://github.com/YOUR-USERNAME/sentinelwatch.git
git push -u origin main       # upload
```
Expected: your files appear on GitHub.

## Step 3 - Create the local database (pgAdmin)
Right-click **Databases > Create > Database**, name it `sentinelwatch`, Save.

## Step 4 - Run the backend (PowerShell)
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1          # prompt now starts with (venv)
pip install -r requirements.txt
copy .env.example .env
```
Generate two random secrets and paste them into `.env` (SECRET_KEY, AGENT_API_KEY):
```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
Edit `.env`: set `DATABASE_URL` with your postgres password, and set `ADMIN_PASSWORD` (12+ characters). Then:
```powershell
uvicorn app.main:app --reload
```
**Test:** browser -> http://localhost:8000/api/health  
**Expected:** `{"status":"ok","database":"connected"}`  
Interactive docs: http://localhost:8000/docs. Tables (`users`, `security_events`, `alerts`, `audit_logs`) are created automatically; check in pgAdmin under Schemas > public > Tables.

Run the automated tests (new PowerShell, same folder, venv active):
```powershell
pytest -q
```
**Expected:** `10 passed`.

## Step 5 - Test the API with curl and Postman
Use YOUR agent key from `.env`:
```powershell
curl.exe -X POST http://localhost:8000/api/events -H "Content-Type: application/json" -H "X-API-Key: YOUR_AGENT_API_KEY" -d "{\"username\":\"admin\",\"source_ip\":\"10.0.2.15\",\"event_type\":\"login_failed\",\"device_name\":\"Kali-VM\",\"operating_system\":\"Kali Linux\"}"
```
Expected: JSON with `"id":1` and status 201. Without the key you get 401; with `"source_ip":"abc"` you get 422.
Postman: New > HTTP > POST same URL > Headers `X-API-Key` > Body raw JSON.
For read endpoints, first POST form data to `/api/auth/login` (username/password) and send `Authorization: Bearer <token>`.

## Step 6 - Test brute-force detection
Send the failed-login event 5 times within 2 minutes (run the curl command 5 times or use the agent in Step 8).
Then log in via http://localhost:8000/docs (Authorize button) and call `GET /api/alerts`.
Expected: one HIGH BRUTE_FORCE alert with `failed_attempts: 5`; at 10 it upgrades to CRITICAL.

## Step 7 - Run the dashboard (new PowerShell)
```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```
Open http://localhost:5173 and sign in with `admin` / your ADMIN_PASSWORD.
Run the agent and watch the cards, charts and alerts update (auto-refresh every 10s).

## Step 8 - Agent (Kali terminal, or Windows for a first test)
```bash
cd agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env                 # set API_URL and AGENT_API_KEY
python security_agent.py                          # menu
python security_agent.py --mode burst --count 6   # one-shot
```
Expected output: `[+] Event generated` / `[+] Sending event...` / `[+] API response: 201` / `[+] Event stored successfully`.
To test from the Kali VM to your Windows host before deploying: use the host's LAN IP in API_URL and start the backend with `uvicorn app.main:app --host 0.0.0.0` (lab network only).

## Step 9 - Deploy PostgreSQL + backend (Render; Railway is similar)
Free tiers and limits change, so check the provider's current pricing page first.
1. Push your latest code to GitHub.
2. Render > **New > PostgreSQL**. Create it and copy the **Internal Database URL**.
3. Render > **New > Web Service** > connect the repo.
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment variables: `DATABASE_URL` (paste the URL), `SECRET_KEY`, `AGENT_API_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `CORS_ORIGINS` (set after Step 10), plus optional detection settings. Use NEW random secrets, not your local ones.
5. Deploy. Open `https://YOUR-SERVICE.onrender.com/api/health`.
**Expected:** `{"status":"ok","database":"connected"}`. Only after you see this is the backend truly deployed.

## Step 10 - Deploy the frontend (Vercel)
1. Vercel > **Add New Project** > import the repo.
2. Root Directory: `frontend`. Framework: Vite.
3. Environment variable: `VITE_API_URL=https://YOUR-SERVICE.onrender.com`
4. Deploy and copy the Vercel URL.
5. Back in Render, set `CORS_ORIGINS=https://YOUR-APP.vercel.app` (exact URL, no trailing slash) and redeploy the backend.
**Expected:** the live dashboard loads and you can sign in.

## Step 11 - Connect Kali to the LIVE API
In Kali `agent/.env`:
```
API_URL=https://YOUR-SERVICE.onrender.com/api/events
AGENT_API_KEY=<the production agent key>
```
Run `python security_agent.py --mode burst --count 6`. Expected: 201 responses, then a HIGH alert on the live dashboard.
(Free-tier services may sleep when idle; open /api/health first to wake the service.)

## Step 12 - Final demonstration
1. Open live dashboard, sign in. 2. Open Kali terminal. 3. Run the agent burst (6 events).
4. Show the 201 responses. 5. Show events in the Events tab (and rows in PostgreSQL).
6. Refresh dashboard: HIGH alert appears. 7. Send 5 more events: it escalates to CRITICAL.
8. Set the alert to RESOLVED. 9. Explain the architecture.

## Step 13 - Evidence (screenshots/ folder)
Capture: health endpoint, `/docs` page, pytest `10 passed`, agent output, dashboard with alert, alert resolved, Render/Vercel deployment pages, pgAdmin tables, GitHub repo.

## Security features
| Feature | Where |
|---|---|
| Password hashing (bcrypt) | `security.py` |
| JWT tokens + roles | `security.py`, `routers/auth.py` |
| Agent API key (constant-time compare) | `verify_agent_key` |
| Input validation (Pydantic, real IP check) | `schemas.py` |
| SQL injection prevention (ORM) | all queries use SQLAlchemy |
| CORS allow-list | `main.py` |
| Security headers | `main.py` |
| Login rate limit (10/min/IP) | `rate_limit` |
| Audit log table | `AuditLog` |
| No secrets in code, `.env` git-ignored | `config.py`, `.gitignore` |
| Passwords never logged | `routers/auth.py` |

## Known limitations
In-memory rate limiter (single instance only), no password reset, no email/SMS alerts, tables created with `create_all` instead of migrations (Alembic is the upgrade path), JWT stored in sessionStorage.

## Future improvements
Alembic migrations, WebSocket live updates, email/Slack alerts, IP geolocation, per-user lockout, real log collection (parsing `/var/log/auth.log` on your own VM), Docker.
