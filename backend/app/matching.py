"""The matching engine.

AI reads adverts and turns them into Rules (see pipeline/). The matching itself is plain,
deterministic rule checks, so every yes or no comes with a reason a person can understand.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from .models import (
    BlockedListing,
    Match,
    MatchReport,
    Opportunity,
    Profile,
    RuleResult,
    Unlock,
)

# A certified copy older than this is usually rejected by South African employers.
CERTIFIED_COPY_MAX_AGE_DAYS = 90
# Show near misses only when this many rules or fewer fail.
NEAR_MISS_MAX_FAILURES = 1


def _norm(text: str) -> str:
    return text.strip().lower()


def check_rules(profile: Profile, opp: Opportunity) -> list[RuleResult]:
    """Check every rule of an opportunity against a profile, with a reason for each."""
    r = opp.rules
    results: list[RuleResult] = []

    if r.fields_of_study:
        ok = profile.field_of_study is not None and _norm(profile.field_of_study) in {
            _norm(f) for f in r.fields_of_study
        }
        results.append(RuleResult(
            rule="field_of_study",
            passed=ok,
            reason=f"Needs a qualification in {', '.join(r.fields_of_study)}; "
                   f"you studied {profile.field_of_study or 'nothing listed'}.",
        ))

    if r.min_qualification:
        ok = profile.qualification.level >= r.min_qualification.level
        results.append(RuleResult(
            rule="min_qualification",
            passed=ok,
            reason=f"Needs at least a {r.min_qualification.value}; you have a {profile.qualification.value}.",
        ))

    if r.min_average is not None:
        ok = profile.average is not None and profile.average >= r.min_average
        results.append(RuleResult(
            rule="min_average",
            passed=ok,
            reason=f"Needs an average of {r.min_average}% or more; yours is "
                   f"{f'{profile.average}%' if profile.average is not None else 'not listed'}.",
        ))

    if r.employment_status:
        allowed = [s.value for s in r.employment_status]
        ok = profile.employment_status.value in allowed
        results.append(RuleResult(
            rule="employment_status",
            passed=ok,
            reason=f"Open to people who are {' or '.join(allowed)}; you are {profile.employment_status.value}.",
        ))

    if r.max_experience_months is not None:
        ok = profile.experience_months <= r.max_experience_months
        results.append(RuleResult(
            rule="max_experience_months",
            passed=ok,
            reason=f"Allows at most {r.max_experience_months} months' work experience; "
                   f"you have {profile.experience_months}.",
        ))

    if r.no_previous_graduate_programme:
        ok = not profile.been_on_graduate_programme
        results.append(RuleResult(
            rule="no_previous_graduate_programme",
            passed=ok,
            reason="Only for people who have never been on a graduate programme"
                   + ("." if ok else "; you have been on one."),
        ))

    if r.provinces:
        ok = _norm(profile.province) in {_norm(p) for p in r.provinces}
        results.append(RuleResult(
            rule="province",
            passed=ok,
            reason=f"Open to {', '.join(r.provinces)}; you live in {profile.province}.",
        ))

    if r.min_age is not None or r.max_age is not None:
        lo = r.min_age if r.min_age is not None else 0
        hi = r.max_age if r.max_age is not None else 200
        ok = lo <= profile.age <= hi
        results.append(RuleResult(
            rule="age",
            passed=ok,
            reason=f"Age {lo}–{hi}; you are {profile.age}." if r.max_age is not None
                   else f"Age {lo} or older; you are {profile.age}.",
        ))

    have = {_norm(c) for c in profile.certificates}
    for cert in r.required_certificates:
        ok = _norm(cert) in have
        results.append(RuleResult(
            rule=f"certificate:{cert}",
            passed=ok,
            reason=f"Needs the {cert} certificate" + ("; you have it." if ok else "; you don't have it yet."),
        ))

    return results


def document_readiness(profile: Profile, opp: Opportunity, today: date) -> tuple[int, list[str]]:
    """Percent of required documents that are ready, and which are missing or out of date."""
    if not opp.documents_required:
        return 100, []
    have = {_norm(d.type): d for d in profile.documents}
    missing: list[str] = []
    for doc in opp.documents_required:
        found = have.get(_norm(doc))
        if found is None:
            missing.append(doc)
        elif _norm(doc).startswith("certified") and found.issued is not None:
            if (today - found.issued).days > CERTIFIED_COPY_MAX_AGE_DAYS:
                missing.append(f"{doc} (older than 3 months, recertify it)")
    ready = len(opp.documents_required) - len(missing)
    return round(100 * ready / len(opp.documents_required)), missing


def match(profile: Profile, opportunities: list[Opportunity], today: date | None = None) -> MatchReport:
    """Match one profile against all opportunities."""
    today = today or date.today()
    eligible: list[Match] = []
    near: list[Match] = []
    blocked: list[BlockedListing] = []
    unlock_map: dict[str, list[str]] = defaultdict(list)

    for opp in opportunities:
        if opp.asks_for_fee:
            blocked.append(BlockedListing(
                opportunity_id=opp.id,
                title=opp.title,
                reason="This listing asks applicants to pay a fee. Real employers never charge to apply.",
            ))
            continue
        if opp.closes < today:
            continue

        results = check_rules(profile, opp)
        failures = [x for x in results if not x.passed]
        readiness, missing = document_readiness(profile, opp, today)
        m = Match(
            opportunity=opp,
            eligible=not failures,
            results=results,
            readiness=readiness,
            missing_documents=missing,
            days_left=(opp.closes - today).days,
        )

        if not failures:
            eligible.append(m)
        else:
            if len(failures) <= NEAR_MISS_MAX_FAILURES:
                near.append(m)
            # Unlock: opportunities where the ONLY things missing are certificates.
            if all(f.rule.startswith("certificate:") for f in failures):
                for f in failures:
                    unlock_map[f.rule.split(":", 1)[1]].append(opp.id)

    eligible.sort(key=lambda m: m.days_left)
    near.sort(key=lambda m: m.days_left)
    unlocks = sorted(
        (Unlock(certificate=c, opens=len(ids), opportunity_ids=ids) for c, ids in unlock_map.items()),
        key=lambda u: -u.opens,
    )
    return MatchReport(eligible=eligible, near_misses=near, unlocks=unlocks, blocked=blocked)
