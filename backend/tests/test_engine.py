import pytest
from app.engine import check_criterion, evaluate, inr, validate_criterion

P = {"state": "Maharashtra", "category": "SC", "gender": "Female", "income": 250000,
     "course_level": "UG", "year": 2, "marks": 60.0, "disability": False, "minority": True}


def test_inr_format():
    assert inr(250000) == "Rs 2,50,000"
    assert inr(1500000) == "Rs 15,00,000"
    assert inr(900) == "Rs 900"


@pytest.mark.parametrize("income,expected", [(249999, True), (250000, True), (250001, False)])
def test_income_boundary(income, expected):
    r = check_criterion("income", "<=", "250000", {**P, "income": income})
    assert r["passed"] is expected


@pytest.mark.parametrize("marks,expected", [(59.9, False), (60, True), (60.1, True)])
def test_marks_boundary(marks, expected):
    assert check_criterion("marks", ">=", "60", {**P, "marks": marks})["passed"] is expected


def test_failed_income_message_is_explained():
    r = check_criterion("income", "<=", "250000", {**P, "income": 300000})
    assert r["passed"] is False
    assert r["message"] == "Income limit is Rs 2,50,000; yours is Rs 3,00,000"


def test_category_list_case_insensitive():
    assert check_criterion("category", "in", "SC,ST", {**P, "category": "sc"})["passed"] is True
    r = check_criterion("category", "in", "SC,ST", {**P, "category": "OBC"})
    assert r["passed"] is False and "SC, ST" in r["message"]


def test_missing_field_fails_without_crash():
    r = check_criterion("income", "<=", "250000", {**P, "income": None})
    assert r["passed"] is False and "not provided" in r["message"]
    r2 = check_criterion("state", "in", "Kerala", {k: v for k, v in P.items() if k != "state"})
    assert r2["passed"] is False


def test_boolean_fields():
    assert check_criterion("minority", "==", "yes", P)["passed"] is True
    assert check_criterion("disability", "==", "yes", P)["passed"] is False


def test_all_criteria_must_pass():
    crit = [{"field": "income", "operator": "<=", "value": "250000"},
            {"field": "category", "operator": "in", "value": "SC,ST"},
            {"field": "marks", "operator": ">=", "value": "60"}]
    assert evaluate(crit, P)["eligible"] is True
    out = evaluate(crit, {**P, "income": 300000})
    assert out["eligible"] is False and out["failed_count"] == 1 and out["near_miss"] is True
    out2 = evaluate(crit, {**P, "income": 300000, "marks": 40})
    assert out2["failed_count"] == 2 and out2["near_miss"] is False


def test_worked_example_from_slides():
    """Income 3 lakh, SC, marks 72 vs income<=2.5 lakh, SC/ST, marks>=60 -> only income fails."""
    crit = [{"field": "income", "operator": "<=", "value": "250000"},
            {"field": "category", "operator": "in", "value": "SC,ST"},
            {"field": "marks", "operator": ">=", "value": "60"}]
    out = evaluate(crit, {**P, "income": 300000, "marks": 72})
    assert [r["passed"] for r in out["results"]] == [False, True, True]


@pytest.mark.parametrize("field,op,val", [("income", "in", "1"), ("income", "<=", "abc"),
                                          ("minority", "==", "maybe"), ("shoe_size", "==", "9"),
                                          ("state", "<=", "Kerala")])
def test_validate_rejects_bad_rows(field, op, val):
    with pytest.raises(ValueError):
        validate_criterion(field, op, val)


def test_validate_accepts_good_rows():
    validate_criterion("income", "<=", "250000")
    validate_criterion("category", "in", "SC,ST")
    validate_criterion("disability", "==", "yes")
