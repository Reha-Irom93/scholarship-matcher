"""Load scholarships.csv and criteria.csv into the database.
Usage (from the backend folder):  python ../data/load.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "backend"))

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.seed import load_csv  # noqa: E402

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    n = load_csv(db, HERE / "scholarships.csv", HERE / "criteria.csv", replace=True)
    print(f"Loaded {n} scholarships")
