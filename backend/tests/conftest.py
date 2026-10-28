import os
import tempfile
from pathlib import Path

# Use an isolated temporary database for every test run (never the real one).
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp) / 'test.db'}"
os.environ["AUTOLOAD_SAMPLE"] = "0"
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-pass"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import load_csv  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    load_csv(db, DATA / "scholarships.csv", DATA / "criteria.csv", replace=True)
    db.close()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_headers(client):
    r = client.post("/admin/login", json={"username": "admin", "password": "test-pass"})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["access_token"]}
