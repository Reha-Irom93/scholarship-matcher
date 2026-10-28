"""Rules engine: checks every criterion of a scholarship against a student profile and
returns a reason for each one. No database access and no stored student data here."""
from typing import Any, Dict, List, Optional

NUMERIC = {"income": "Income", "marks": "Marks", "year": "Year of study"}
CATEGORICAL = {"state": "State", "category": "Category", "gender": "Gender", "course_level": "Course level"}
BOOLEAN = {"disability": "Disability", "minority": "Minority status"}
FIELDS = {**NUMERIC, **CATEGORICAL, **BOOLEAN}
OPERATORS_FOR = {
    "numeric": {"<=", ">=", "=="},
    "categorical": {"==", "in"},
    "boolean": {"=="},
}


def field_kind(field: str) -> str:
    if field in NUMERIC:
        return "numeric"
    if field in CATEGORICAL:
        return "categorical"
    if field in BOOLEAN:
        return "boolean"
    raise ValueError(f"Unknown field: {field}")


def validate_criterion(field: str, operator: str, value: str) -> None:
    """Raise ValueError if a criterion row is not usable by the engine (used by the admin API)."""
    kind = field_kind(field)
    if operator not in OPERATORS_FOR[kind]:
        raise ValueError(f"Operator '{operator}' is not allowed for {field}")
    if kind == "numeric":
        float(value)  # ValueError if not a number
    elif kind == "boolean" and value.strip().lower() not in {"yes", "no"}:
        raise ValueError(f"{field} value must be yes or no")
    elif kind == "categorical" and not [v for v in value.split(",") if v.strip()]:
        raise ValueError(f"{field} needs at least one value")


def inr(n: float) -> str:
    """Indian digit grouping, e.g. 250000 -> Rs 2,50,000."""
    n = int(round(n))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return "Rs " + ("-" if n < 0 else "") + s


def _fmt_num(field: str, x: float) -> str:
    if field == "income":
        return inr(x)
    if field == "marks":
        return f"{x:g}%"
    return f"{x:g}"


def _norm_profile_value(field: str, v: Any) -> Optional[str]:
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if field in BOOLEAN:
        if isinstance(v, bool):
            return "yes" if v else "no"
        return str(v).strip().lower()
    return str(v).strip()


def check_criterion(field: str, operator: str, value: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    label = FIELDS[field]
    kind = field_kind(field)
    raw = profile.get(field)
    actual = _norm_profile_value(field, raw)
    out = {"field": field, "label": label, "operator": operator, "required": value, "actual": actual}

    if actual is None:
        out.update(passed=False, message=f"{label} was not provided")
        return out

    if kind == "numeric":
        a, r = float(actual), float(value)
        if operator == "<=":
            ok = a <= r
            msg_ok = f"{label} {_fmt_num(field, a)} is within the limit of {_fmt_num(field, r)}"
            msg_no = f"{label} limit is {_fmt_num(field, r)}; yours is {_fmt_num(field, a)}"
        elif operator == ">=":
            ok = a >= r
            msg_ok = f"{label} {_fmt_num(field, a)} meets the minimum of {_fmt_num(field, r)}"
            msg_no = f"{label} must be at least {_fmt_num(field, r)}; yours is {_fmt_num(field, a)}"
        else:
            ok = a == r
            msg_ok = f"{label} {_fmt_num(field, a)} matches the requirement"
            msg_no = f"{label} must be {_fmt_num(field, r)}; yours is {_fmt_num(field, a)}"
        out.update(passed=ok, message=msg_ok if ok else msg_no)
        out["actual"] = _fmt_num(field, a)
        return out

    if kind == "boolean":
        want = value.strip().lower()
        ok = actual == want
        msg_ok = f"{label}: {want} matches the requirement"
        msg_no = f"{label} must be '{want}'; yours is '{actual}'"
        out.update(passed=ok, message=msg_ok if ok else msg_no)
        return out

    # categorical
    options = [v.strip() for v in value.split(",") if v.strip()]
    ok = actual.lower() in [o.lower() for o in options]
    shown = ", ".join(options)
    if operator == "in" or len(options) > 1:
        msg_ok = f"{label} '{actual}' is allowed ({shown})"
        msg_no = f"{label} must be one of {shown}; yours is '{actual}'"
    else:
        msg_ok = f"{label} '{actual}' matches the requirement"
        msg_no = f"{label} must be {shown}; yours is '{actual}'"
    out.update(passed=ok, message=msg_ok if ok else msg_no)
    return out


def evaluate(criteria: List[Dict[str, str]], profile: Dict[str, Any]) -> Dict[str, Any]:
    """All criteria must pass (AND). near_miss = exactly one criterion failed."""
    results = [check_criterion(c["field"], c["operator"], c["value"], profile) for c in criteria]
    failed = [r for r in results if not r["passed"]]
    return {
        "eligible": len(failed) == 0,
        "failed_count": len(failed),
        "near_miss": len(failed) == 1,
        "results": results,
    }
