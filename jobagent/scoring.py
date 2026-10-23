"""Evidence-based ranking. Every match remains for human review; never applies."""
from __future__ import annotations
import re
import unicodedata


def normal(text: object) -> str:
    return "".join(x for x in unicodedata.normalize("NFKD", str(text or "").casefold()) if not unicodedata.combining(x))


def includes_term(haystack: str, term: str) -> bool:
    haystack = normal(haystack)
    term = normal(term).strip()
    if not term:
        return False
    return bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", haystack))


def assess(job: dict, profile: dict) -> dict:
    """Score 0-100: ranking signal, NOT hiring probability or permission to apply."""
    title = normal(job.get("title", ""))
    description = normal(job.get("description", ""))[:15000]
    loc = normal(job.get("location", ""))
    workplace = normal(job.get("workplace_type", ""))
    text = f"{loc} {workplace} {description}"
    title_hits = [x for x in profile["priority_terms"] if includes_term(title, x)]
    skills = [x for x in profile["confirmed_skills"] if includes_term(description, x)]
    score = min(40, 20 * len(title_hits)) + min(40, 10 * len(skills))
    blockers: list[str] = []
    unknowns: list[str] = []

    # Do not infer remote eligibility from global company branding or absence of a location.
    remote = bool(re.search(r"\bremote\b|\bremot[oa]\b|home office", text))
    hybrid = bool(re.search(r"\bhybrid\b|\bhibrid[oa]\b|on.?site|presencial", text))
    if profile.get("preferred_workplace") == "remote":
        if workplace in ("hybrid", "on-site", "onsite", "presencial") or (hybrid and not remote):
            blockers.append("Explicitly non-remote or hybrid workplace")
        elif remote:
            score += 10
        else:
            unknowns.append("Remote workplace not established")
    elif remote:
        score += 10

    countries = profile.get("country_keywords", [])
    if countries:
        if any(includes_term(text, c) for c in countries):
            score += 10
        else:
            unknowns.append("Country eligibility not established")

    if re.search(r"\b(?:us only|united states only|must reside in the us|only in canada)\b", text):
        blockers.append("Explicit location restriction outside target country")

    # We do not estimate salaries from free-form text; only explicit structured BRL/month.
    sal = job.get("salary_structured") or {}
    salary = None
    contract = str(job.get("contract_type", "UNKNOWN")).upper()
    if isinstance(sal, dict) and str(sal.get("currency", "")).upper() == "BRL" and str(sal.get("interval", "")).lower() in ("month", "monthly"):
        try:
            salary = float(sal["min"])
            if not 0 < salary < 10**9:
                salary = None
        except (KeyError, TypeError, ValueError):
            pass
    minimums = profile.get("minimum_monthly_brl", {})
    minimum = minimums.get(contract)
    if salary is None:
        unknowns.append("Monthly BRL salary not confirmed")
    elif minimum is None:
        unknowns.append("Minimum salary for this contract not configured")
    elif salary < minimum:
        blockers.append("Salary below configured minimum")
    if contract == "UNKNOWN":
        unknowns.append("Contract type not confirmed")
    if not title_hits:
        blockers.append("Job title outside configured target families")

    score = min(100, score)
    threshold = profile["review_score_threshold"]
    status = "BLOCKED" if blockers else "REVIEW" if score >= threshold else "LOW_MATCH"
    return {"score": score, "status": status, "blockers": blockers, "unknowns": unknowns,
            "matched_title_terms": title_hits, "matched_skills": skills,
            "salary_brl_monthly": salary, "contract_type": contract, "auto_apply": False}
