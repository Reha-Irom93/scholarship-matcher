import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import auth, engine as rules
from .db import Base, SessionLocal, engine as db_engine, get_db
from .models import Criterion, Scholarship
from .schemas import LoginIn, ScholarshipIn, ScholarshipOut, StudentProfile
from .seed import load_csv

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=db_engine)
    if os.getenv("AUTOLOAD_SAMPLE", "1") == "1":
        db = SessionLocal()
        try:
            if db.query(Scholarship).count() == 0 and (DATA_DIR / "scholarships.csv").exists():
                load_csv(db, DATA_DIR / "scholarships.csv", DATA_DIR / "criteria.csv", replace=False)
        finally:
            db.close()
    yield


app = FastAPI(title="Scholarship Matcher API", version="1.0.0", lifespan=lifespan,
              description="Prototype: rule-based scholarship matching with explanations.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173").split(","),
    allow_methods=["*"], allow_headers=["*"],
)


def _summary(s: Scholarship) -> dict:
    return {"id": s.id, "name": s.name, "provider": s.provider, "level": s.level,
            "official_link": s.official_link, "deadline": s.deadline,
            "benefit_amount": s.benefit_amount, "description": s.description,
            "source_link": s.source_link, "verified_on": s.verified_on, "is_sample": s.is_sample}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/match")
def match(profile: StudentProfile, db: Session = Depends(get_db)):
    """Student details are used only inside this request and are never stored or logged."""
    data = profile.model_dump()
    eligible, not_eligible = [], []
    for s in db.query(Scholarship).all():
        ev = rules.evaluate([{"field": c.field, "operator": c.operator, "value": c.value} for c in s.criteria], data)
        item = {**_summary(s), **ev}
        (eligible if ev["eligible"] else not_eligible).append(item)
    eligible.sort(key=lambda x: (x["deadline"], x["name"]))
    not_eligible.sort(key=lambda x: (x["failed_count"], x["deadline"], x["name"]))
    return {
        "counts": {"eligible": len(eligible), "not_eligible": len(not_eligible),
                   "near_miss": sum(1 for x in not_eligible if x["near_miss"]),
                   "total": len(eligible) + len(not_eligible)},
        "eligible": eligible, "not_eligible": not_eligible,
    }


@app.get("/scholarships", response_model=List[ScholarshipOut])
def list_scholarships(level: Optional[str] = None, state: Optional[str] = None, provider: Optional[str] = None,
                      deadline_before: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
                      q: Optional[str] = None, db: Session = Depends(get_db)):
    rows = db.query(Scholarship).order_by(Scholarship.deadline, Scholarship.name).all()
    out = []
    for s in rows:
        if level and level.lower() not in s.level.lower():
            continue
        if provider and provider.lower() not in s.provider.lower():
            continue
        if deadline_before and s.deadline > deadline_before:
            continue
        if q and q.lower() not in (s.name + " " + s.description).lower():
            continue
        if state:
            state_rules = [c for c in s.criteria if c.field == "state"]
            if state_rules and not any(state.lower() in [v.strip().lower() for v in c.value.split(",")] for c in state_rules):
                continue
        out.append(s)
    return out


@app.get("/scholarships/{sid}", response_model=ScholarshipOut)
def get_scholarship(sid: int, db: Session = Depends(get_db)):
    s = db.get(Scholarship, sid)
    if not s:
        raise HTTPException(404, "Scholarship not found")
    return s


@app.post("/admin/login")
def login(body: LoginIn):
    if not auth.check_login(body.username, body.password):
        raise HTTPException(401, "Wrong username or password")
    return {"access_token": auth.make_token(body.username), "token_type": "bearer"}


def _apply(s: Scholarship, body: ScholarshipIn) -> None:
    for k in ("name", "provider", "level", "official_link", "deadline", "benefit_amount",
              "description", "source_link", "verified_on", "is_sample"):
        setattr(s, k, getattr(body, k))
    s.criteria = [Criterion(field=c.field, operator=c.operator, value=c.value) for c in body.criteria]


@app.post("/scholarships", response_model=ScholarshipOut, status_code=201)
def create_scholarship(body: ScholarshipIn, db: Session = Depends(get_db), _: str = Depends(auth.require_admin)):
    s = Scholarship()
    _apply(s, body)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@app.put("/scholarships/{sid}", response_model=ScholarshipOut)
def update_scholarship(sid: int, body: ScholarshipIn, db: Session = Depends(get_db), _: str = Depends(auth.require_admin)):
    s = db.get(Scholarship, sid)
    if not s:
        raise HTTPException(404, "Scholarship not found")
    _apply(s, body)
    db.commit()
    db.refresh(s)
    return s


@app.delete("/scholarships/{sid}", status_code=204)
def delete_scholarship(sid: int, db: Session = Depends(get_db), _: str = Depends(auth.require_admin)):
    s = db.get(Scholarship, sid)
    if not s:
        raise HTTPException(404, "Scholarship not found")
    db.delete(s)
    db.commit()
