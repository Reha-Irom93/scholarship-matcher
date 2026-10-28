"""Load scholarships.csv + criteria.csv (spreadsheet -> CSV -> database)."""
import csv
from pathlib import Path
from sqlalchemy.orm import Session
from .engine import validate_criterion
from .models import Scholarship, Criterion


def load_csv(db: Session, scholarships_csv: Path, criteria_csv: Path, replace: bool = True) -> int:
    if replace:
        db.query(Criterion).delete()
        db.query(Scholarship).delete()
        db.commit()
    with open(scholarships_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            db.add(Scholarship(
                id=int(row["id"]), name=row["name"], provider=row["provider"], level=row["level"],
                official_link=row["official_link"], deadline=row["deadline"],
                benefit_amount=int(row["benefit_amount"]), description=row.get("description", ""),
                source_link=row.get("source_link", ""), verified_on=row.get("verified_on", ""),
                is_sample=row.get("is_sample", "1") in {"1", "true", "True", "yes"},
            ))
    db.flush()
    with open(criteria_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            validate_criterion(row["field"], row["operator"], row["value"])  # reject bad rows early
            db.add(Criterion(scholarship_id=int(row["scholarship_id"]), field=row["field"],
                             operator=row["operator"], value=row["value"]))
    db.commit()
    return db.query(Scholarship).count()
