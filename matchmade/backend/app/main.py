"""Match Made API.

Run locally:  uvicorn app.main:app --reload   (from the backend/ folder)
Docs:         http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI

from .matching import match
from .models import MatchReport, Opportunity, Profile

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "opportunities.json"

app = FastAPI(
    title="Match Made API",
    description="Shows young South Africans only the opportunities they qualify for, "
                "and the one step that opens the next.",
    version="0.1.0",
)


def load_opportunities() -> list[Opportunity]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [Opportunity.model_validate(item) for item in raw]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/opportunities", response_model=list[Opportunity])
def list_opportunities() -> list[Opportunity]:
    """All verified opportunities (demo data)."""
    return load_opportunities()


@app.post("/match", response_model=MatchReport)
def match_profile(profile: Profile, today: date | None = None) -> MatchReport:
    """Match a profile: eligible opportunities, near misses, unlock steps and blocked scams."""
    return match(profile, load_opportunities(), today=today)
