# SentinelWatch API

Base URL: `http://localhost:8000` (local) or your Render URL. Interactive docs: `/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /api/health | none | API and database status |
| POST | /api/auth/login | none (form: username, password) | Returns JWT |
| GET | /api/auth/me | Bearer | Current user |
| POST | /api/users | Bearer (ADMIN) | Create user |
| POST | /api/events | `X-API-Key` | Ingest event (201); runs detection |
| GET | /api/events | Bearer | List events (`limit`, `offset`, `event_type`, `source_ip`) |
| GET | /api/events/{id} | Bearer | One event |
| GET | /api/alerts | Bearer | List alerts (`status`, `severity`, `limit`) |
| GET | /api/alerts/{id} | Bearer | One alert |
| PATCH | /api/alerts/{id} | Bearer | Body `{"status":"OPEN|INVESTIGATING|RESOLVED"}` |
| GET | /api/dashboard/stats | Bearer | Cards, chart data, recent items |

Errors: 401 unauthorized, 403 forbidden, 404 not found, 422 validation (`{"detail","errors":[{field,message}]}`), 429 rate limited, 500 generic.

Event body: `username`, `source_ip` (valid IP), `event_type` (login_success, login_failed, logout, suspicious_login, account_locked), optional `timestamp`, `device_name`, `operating_system`, `message`.
