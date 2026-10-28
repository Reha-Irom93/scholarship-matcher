# Scholarship Matcher (prototype)

Rule-based scholarship eligibility matcher with per-criterion explanations.
React + Vite frontend, FastAPI backend, SQLite (PostgreSQL via DATABASE_URL, not tested).

**All 30 scholarships in data/ are SAMPLE records, not real schemes.** Replace them with
verified official data (fill source_link and verified_on) before any real use.

## Run
Backend (Python 3.10+):
    cd backend && pip install -r requirements.txt
    uvicorn app.main:app --port 8000        # auto-loads sample CSV on first start
Frontend (Node 18+):
    cd frontend && npm install && npm run dev      # http://localhost:5173

Admin login (demo only): admin / admin123. Override with ADMIN_USER, ADMIN_PASSWORD, SECRET_KEY.

## Tests
    cd backend && python -m pytest -v      # 41 tests; see docs/test_report.txt

## Data format
data/scholarships.csv and data/criteria.csv. A criterion is (field, operator, value):
income/marks/year use <=, >=, ==; state/category/gender/course_level use in or ==; disability/minority use == yes/no.
A scholarship is eligible only if ALL criteria pass. "Near miss" = exactly one criterion failed.

## Measured (sandbox, see docs/)
41/41 tests pass; POST /match median 9.7 ms, p95 12.8 ms (200 requests, 30 records, SQLite, localhost).
Not measured: comparison with manual search, real-user feedback, PostgreSQL.

## Privacy
Student details are processed per request and not stored (only scholarships and criteria tables exist).
