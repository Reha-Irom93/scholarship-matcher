from app.db import SessionLocal
from app.models import Scholarship

PROFILE = {"state": "Maharashtra", "category": "SC", "gender": "Male", "income": 200000,
           "course_level": "UG", "year": 2, "marks": 72, "disability": False, "minority": False}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_match_returns_both_lists_with_reasons(client):
    r = client.post("/match", json=PROFILE)
    assert r.status_code == 200
    d = r.json()
    assert d["counts"]["total"] == 30
    assert d["counts"]["eligible"] == len(d["eligible"])
    first = d["not_eligible"][0]
    assert first["results"] and all("message" in x for x in first["results"])


def test_match_validation_errors(client):
    assert client.post("/match", json={**PROFILE, "category": "XYZ"}).status_code == 422
    assert client.post("/match", json={**PROFILE, "income": -5}).status_code == 422
    assert client.post("/match", json={**PROFILE, "marks": 120}).status_code == 422
    bad = {k: v for k, v in PROFILE.items() if k != "income"}
    assert client.post("/match", json=bad).status_code == 422


def test_match_does_not_store_student_data(client):
    db = SessionLocal()
    before = db.query(Scholarship).count()
    client.post("/match", json=PROFILE)
    after = db.query(Scholarship).count()
    tables = set(__import__("app.db", fromlist=["Base"]).Base.metadata.tables)
    db.close()
    assert before == after
    assert tables == {"scholarships", "criteria"}  # there is no table that could hold student profiles


def test_list_and_filters(client):
    assert len(client.get("/scholarships").json()) == 30
    pg = client.get("/scholarships", params={"level": "PG"}).json()
    assert pg and all("PG" in s["level"] for s in pg)
    mh = {s["name"] for s in client.get("/scholarships", params={"state": "Maharashtra"}).json()}
    assert "Sample Maharashtra Merit-cum-Means Scholarship" in mh
    assert "Sample Karnataka Girls Scholarship" not in mh
    assert "Sample Open Merit Scholarship" in mh   # all-India schemes still apply
    early = client.get("/scholarships", params={"deadline_before": "2027-01-01"}).json()
    assert early and all(s["deadline"] <= "2027-01-01" for s in early)


def test_detail_and_404(client):
    d = client.get("/scholarships/2").json()
    assert d["name"].startswith("Sample Central Post-Matric") and len(d["criteria"]) == 3
    assert client.get("/scholarships/9999").status_code == 404


def test_admin_requires_login(client):
    body = {"name": "X Test", "provider": "P", "level": "UG", "official_link": "https://example.org",
            "deadline": "2027-05-01", "benefit_amount": 1000, "criteria": []}
    assert client.post("/scholarships", json=body).status_code == 401
    assert client.delete("/scholarships/1").status_code == 401
    assert client.put("/scholarships/1", json=body).status_code == 401
    assert client.post("/admin/login", json={"username": "admin", "password": "wrong"}).status_code == 401
    bad = {"Authorization": "Bearer not.a.token"}
    assert client.post("/scholarships", json=body, headers=bad).status_code == 401


def test_admin_crud_and_rules_as_data(client, admin_headers):
    body = {"name": "Brand New Scholarship", "provider": "Test", "level": "UG",
            "official_link": "https://example.org/new", "deadline": "2027-05-01", "benefit_amount": 5000,
            "criteria": [{"field": "income", "operator": "<=", "value": "999999"},
                         {"field": "state", "operator": "in", "value": "Goa"}]}
    r = client.post("/scholarships", json=body, headers=admin_headers)
    assert r.status_code == 201
    sid = r.json()["id"]
    goa = {**PROFILE, "state": "Goa"}
    names = [x["name"] for x in client.post("/match", json=goa).json()["eligible"]]
    assert "Brand New Scholarship" in names      # new rows -> new result, no code change
    body["criteria"][0]["value"] = "100"          # tighten the income rule
    assert client.put(f"/scholarships/{sid}", json=body, headers=admin_headers).status_code == 200
    names = [x["name"] for x in client.post("/match", json=goa).json()["eligible"]]
    assert "Brand New Scholarship" not in names
    assert client.delete(f"/scholarships/{sid}", headers=admin_headers).status_code == 204
    assert client.get(f"/scholarships/{sid}").status_code == 404


def test_admin_rejects_invalid_criteria(client, admin_headers):
    body = {"name": "Bad Rule", "provider": "T", "level": "UG", "official_link": "https://example.org",
            "deadline": "2027-05-01", "benefit_amount": 1,
            "criteria": [{"field": "income", "operator": "in", "value": "abc"}]}
    assert client.post("/scholarships", json=body, headers=admin_headers).status_code == 422
    body["criteria"] = [{"field": "shoe_size", "operator": "==", "value": "9"}]
    assert client.post("/scholarships", json=body, headers=admin_headers).status_code == 422
