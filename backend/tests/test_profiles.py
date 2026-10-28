"""10 sample student profiles. For each one the engine's eligible list is compared with
(a) an independent reference check written with plain Python operators straight from the CSV
(it does not import the engine), and (b) three lists derived by hand (P1, P3, P10)."""
import csv
import operator
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[2] / "data"

PROFILES = {
    "P1": dict(state="Maharashtra", category="SC", gender="Male", income=200000, course_level="UG", year=2, marks=72, disability=False, minority=False),
    "P2": dict(state="Karnataka", category="General", gender="Female", income=450000, course_level="UG", year=3, marks=80, disability=False, minority=False),
    "P3": dict(state="Uttar Pradesh", category="OBC", gender="Male", income=120000, course_level="Diploma", year=1, marks=58, disability=False, minority=False),
    "P4": dict(state="Delhi", category="General", gender="Female", income=280000, course_level="PG", year=1, marks=88, disability=False, minority=True),
    "P5": dict(state="Tamil Nadu", category="EWS", gender="Male", income=700000, course_level="UG", year=4, marks=78, disability=True, minority=False),
    "P6": dict(state="Bihar", category="ST", gender="Female", income=240000, course_level="UG", year=1, marks=62, disability=False, minority=True),
    "P7": dict(state="Gujarat", category="General", gender="Male", income=1200000, course_level="PG", year=2, marks=92, disability=False, minority=False),
    "P8": dict(state="Kerala", category="OBC", gender="Female", income=140000, course_level="Diploma", year=2, marks=66, disability=True, minority=True),
    "P9": dict(state="Rajasthan", category="SC", gender="Female", income=90000, course_level="UG", year=3, marks=70, disability=False, minority=False),
    "P10": dict(state="West Bengal", category="General", gender="Other", income=250000, course_level="UG", year=2, marks=60, disability=False, minority=False),
}
HAND = {"P1": {1, 2, 13, 14}, "P3": {3, 9, 25}, "P10": {1, 20}}


def reference_eligible(profile):
    """Plain-Python reference: reads the CSV rows and applies operators directly."""
    crit = {}
    with open(DATA / "criteria.csv", newline="") as f:
        for r in csv.DictReader(f):
            crit.setdefault(int(r["scholarship_id"]), []).append(r)
    with open(DATA / "scholarships.csv", newline="") as f:
        ids = [int(r["id"]) for r in csv.DictReader(f)]
    ok = set()
    for sid in ids:
        good = True
        for c in crit.get(sid, []):
            have = profile[c["field"]]
            if isinstance(have, bool):
                have = "yes" if have else "no"
            op, val = c["operator"], c["value"]
            if c["field"] in ("income", "marks", "year"):
                f = {"<=": operator.le, ">=": operator.ge, "==": operator.eq}[op]
                good &= f(float(have), float(val))
            else:
                good &= str(have).lower() in [v.strip().lower() for v in val.split(",")]
        if good:
            ok.add(sid)
    return ok


@pytest.mark.parametrize("pid", list(PROFILES))
def test_profile_matches_reference(client, pid):
    got = {x["id"] for x in client.post("/match", json=PROFILES[pid]).json()["eligible"]}
    assert got == reference_eligible(PROFILES[pid])


@pytest.mark.parametrize("pid", list(HAND))
def test_profile_matches_hand_derived(client, pid):
    got = {x["id"] for x in client.post("/match", json=PROFILES[pid]).json()["eligible"]}
    assert got == HAND[pid]
