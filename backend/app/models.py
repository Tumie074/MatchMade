"""Data models for Match Made: young people's profiles, opportunities and match results."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class Qualification(str, Enum):
    matric = "matric"
    certificate = "certificate"
    diploma = "diploma"
    degree = "degree"
    honours = "honours"

    @property
    def level(self) -> int:
        return ["matric", "certificate", "diploma", "degree", "honours"].index(self.value)


class EmploymentStatus(str, Enum):
    unemployed = "unemployed"
    employed = "employed"
    student = "student"


class OpportunityKind(str, Enum):
    graduate_programme = "graduate_programme"
    internship = "internship"
    learnership = "learnership"
    bursary = "bursary"
    job = "job"
    funding = "funding"


class Document(BaseModel):
    """A document the user has, e.g. a CV or a certified ID copy."""

    type: str = Field(examples=["cv", "certified_id", "academic_record"])
    issued: date | None = Field(default=None, description="Date issued or certified, if it matters.")


class Profile(BaseModel):
    """What a young person tells Match Made once. No ID numbers are stored (POPIA)."""

    name: str
    age: int = Field(ge=15, le=40)
    province: str
    qualification: Qualification
    field_of_study: str | None = None
    average: int | None = Field(default=None, ge=0, le=100)
    employment_status: EmploymentStatus
    experience_months: int = Field(default=0, ge=0)
    been_on_graduate_programme: bool = False
    certificates: list[str] = Field(default_factory=list)
    documents: list[Document] = Field(default_factory=list)


class Rules(BaseModel):
    """Eligibility rules extracted from an advert. Every field is optional: None means no rule."""

    fields_of_study: list[str] | None = None
    min_qualification: Qualification | None = None
    min_average: int | None = None
    employment_status: list[EmploymentStatus] | None = None
    max_experience_months: int | None = None
    no_previous_graduate_programme: bool = False
    provinces: list[str] | None = None
    min_age: int | None = None
    max_age: int | None = None
    required_certificates: list[str] = Field(default_factory=list)


class Opportunity(BaseModel):
    id: str
    title: str
    organisation: str
    kind: OpportunityKind
    rules: Rules
    documents_required: list[str] = Field(default_factory=list)
    closes: date
    verified_on: str | None = Field(default=None, description="Where the closing date was checked.")
    url: str | None = None
    asks_for_fee: bool = False


class RuleResult(BaseModel):
    rule: str
    passed: bool
    reason: str


class Match(BaseModel):
    opportunity: Opportunity
    eligible: bool
    results: list[RuleResult]
    readiness: int = Field(description="Percent of required documents that are ready.")
    missing_documents: list[str]
    days_left: int


class Unlock(BaseModel):
    certificate: str
    opens: int = Field(description="How many more opportunities this certificate would open.")
    opportunity_ids: list[str]


class BlockedListing(BaseModel):
    opportunity_id: str
    title: str
    reason: str


class MatchReport(BaseModel):
    eligible: list[Match]
    near_misses: list[Match]
    unlocks: list[Unlock]
    blocked: list[BlockedListing]
