# Test plan
Fill the "Actual Result" and "Status" columns as you run each test. Automated tests: `pytest -q` in `backend/`.

| # | Test Case | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| 1 | GET /api/health | 200, database connected | | |
| 2 | Database connection | Tables visible in pgAdmin | | |
| 3 | POST valid event with key | 201 and event id | | |
| 4 | GET /api/events with token | List including new event | | |
| 5 | POST invalid IP / event type | 422 with field errors | | |
| 6 | 5 failed logins < 2 min | BRUTE_FORCE alert created | | |
| 7 | Alert severity | 5-9 HIGH, 10+ CRITICAL | | |
| 8 | PATCH alert to RESOLVED | resolved_at set | | |
| 9 | GET /api/dashboard/stats | Counts match database | | |
| 10 | Agent from Kali | 201, event stored | | |
| 11 | Login with correct password | Token returned | | |
| 12 | GET /api/events with no token / wrong API key | 401 | | |
| 13 | Analyst calls POST /api/users | 403 | | |
| 14 | Render service /api/health | 200 on public URL | | |
| 15 | Live dashboard + live alert | Alert visible after agent burst | | |
