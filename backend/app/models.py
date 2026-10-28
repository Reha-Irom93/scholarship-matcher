from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .db import Base


class Scholarship(Base):
    __tablename__ = "scholarships"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(200), nullable=False)
    level = Column(String(40), nullable=False)          # UG, PG, Diploma, UG/PG ...
    official_link = Column(String(500), nullable=False)
    deadline = Column(String(10), nullable=False)       # ISO date YYYY-MM-DD
    benefit_amount = Column(Integer, nullable=False)    # rupees per year
    description = Column(Text, default="")
    source_link = Column(String(500), default="")       # page the criteria were taken from
    verified_on = Column(String(10), default="")        # date a human verified the record
    is_sample = Column(Boolean, default=True)           # True = illustrative record, not a real scheme
    criteria = relationship("Criterion", cascade="all, delete-orphan", lazy="selectin",
                            order_by="Criterion.id")


class Criterion(Base):
    __tablename__ = "criteria"
    id = Column(Integer, primary_key=True)
    scholarship_id = Column(Integer, ForeignKey("scholarships.id", ondelete="CASCADE"), nullable=False)
    field = Column(String(40), nullable=False)          # income, category, ...
    operator = Column(String(5), nullable=False)        # <=, >=, ==, in
    value = Column(String(200), nullable=False)         # "250000" or "SC,ST"
