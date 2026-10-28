from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from .engine import FIELDS, validate_criterion


class StudentProfile(BaseModel):
    state: str = Field(min_length=2, max_length=60)
    category: Literal["General", "OBC", "SC", "ST", "EWS"]
    gender: Literal["Male", "Female", "Other"]
    income: int = Field(ge=0, le=100_000_000, description="Annual family income in rupees")
    course_level: Literal["UG", "PG", "Diploma"]
    year: int = Field(ge=1, le=6)
    marks: float = Field(ge=0, le=100, description="Previous-year marks in percent")
    disability: bool = False
    minority: bool = False


class CriterionIn(BaseModel):
    field: str
    operator: str
    value: str

    @model_validator(mode="after")
    def _check(self):
        if self.field not in FIELDS:
            raise ValueError(f"Unknown field '{self.field}'. Use one of: {', '.join(FIELDS)}")
        try:
            validate_criterion(self.field, self.operator, self.value)
        except ValueError as e:
            raise ValueError(str(e))
        return self


class CriterionOut(CriterionIn):
    id: int
    model_config = {"from_attributes": True}


class ScholarshipIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    provider: str = Field(min_length=2, max_length=200)
    level: str = Field(min_length=2, max_length=40)
    official_link: str = Field(min_length=4, max_length=500)
    deadline: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    benefit_amount: int = Field(ge=0)
    description: str = ""
    source_link: str = ""
    verified_on: str = ""
    is_sample: bool = True
    criteria: List[CriterionIn] = []


class ScholarshipOut(BaseModel):
    id: int
    name: str
    provider: str
    level: str
    official_link: str
    deadline: str
    benefit_amount: int
    description: str
    source_link: str
    verified_on: str
    is_sample: bool
    criteria: List[CriterionOut] = []
    model_config = {"from_attributes": True}


class LoginIn(BaseModel):
    username: str
    password: str
