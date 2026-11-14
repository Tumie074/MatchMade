from datetime import date

from fastapi.testclient import TestClient

from app.main import app, load_opportunities
from app.matching import match
from app.models import Document, Profile

TODAY = date(2026, 11, 14)


def thandi(**changes) -> Profile:
    base = dict(
        name="Thandi",
        age=22,
        province="Gauteng",
        qualification="degree",
        field_of_study="IT",
        average=68,
        employment_status="unemployed",
        experience_months=0,
        documents=[
            Document(type="cv"),
            Document(type="academic_record"),
            Document(type="certified_id", issued=date(2026, 6, 1)),  # older than 3 months
        ],
    )
    base.update(changes)
    return Profile(**base)


def ids(matches):
    return {m.opportunity.id for m in matches}


def test_thandi_qualifies_with_reasons():
    report = match(thandi(), load_opportunities(), today=TODAY)
    assert {"lumo-grad-2027", "imbali-learnership", "kasi-founders-grant"} <= ids(report.eligible)
    lumo = next(m for m in report.eligible if m.opportunity.id == "lumo-grad-2027")
    assert all(r.passed and r.reason for r in lumo.results)


def test_old_certified_copy_lowers_readiness():
    report = match(thandi(), load_opportunities(), today=TODAY)
    lumo = next(m for m in report.eligible if m.opportunity.id == "lumo-grad-2027")
    assert lumo.readiness == 67
    assert any("recertify" in d for d in lumo.missing_documents)


def test_low_average_explains_why():
    report = match(thandi(average=60), load_opportunities(), today=TODAY)
    assert "lumo-grad-2027" not in ids(report.eligible)
    lumo = next(m for m in report.near_misses if m.opportunity.id == "lumo-grad-2027")
    failed = [r for r in lumo.results if not r.passed]
    assert failed[0].rule == "min_average"
    assert "65%" in failed[0].reason and "60%" in failed[0].reason


def test_unlock_ranks_certificate_that_opens_most_doors():
    report = match(thandi(), load_opportunities(), today=TODAY)
    top = report.unlocks[0]
    assert top.certificate == "Azure Fundamentals (AZ-900)"
    assert top.opens == 2


def test_certificate_actually_unlocks():
    report = match(thandi(certificates=["Azure Fundamentals (AZ-900)"]), load_opportunities(), today=TODAY)
    assert {"siyakha-cloud-intern", "northgate-data-intern"} <= ids(report.eligible)


def test_scam_is_blocked_and_closed_is_hidden():
    report = match(thandi(), load_opportunities(), today=TODAY)
    assert [b.opportunity_id for b in report.blocked] == ["quickjobs-scam"]
    every = ids(report.eligible) | ids(report.near_misses)
    assert "quickjobs-scam" not in every
    assert "riverbend-grad-closed" not in every


def test_api_match_endpoint():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    res = client.post("/match", params={"today": "2026-11-14"}, json=thandi().model_dump(mode="json"))
    assert res.status_code == 200
    assert res.json()["unlocks"][0]["opens"] == 2
