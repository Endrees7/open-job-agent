from jobagent.config import load_demo_profile
from jobagent.scoring import assess, includes_term

P = load_demo_profile()
BASE = {"id": "x", "title": "Automation & Integration Analyst", "description": "Python API and webhook workflow",
        "location": "Brazil", "workplace_type": "remote", "contract_type": "UNKNOWN"}


def test_title_and_skills_reach_review():
    a = assess(BASE, P)
    assert a["status"] == "REVIEW"
    assert a["auto_apply"] is False
    assert "Monthly BRL salary not confirmed" in a["unknowns"]


def test_hybrid_blocks_remote_only():
    a = assess(dict(BASE, workplace_type="hybrid", location="Hybrid Brazil"), P)
    assert a["status"] == "BLOCKED"


def test_unknown_country_stays_unknown():
    a = assess(dict(BASE, location="Unknown"), P)
    assert "Country eligibility not established" in a["unknowns"]


def test_explicit_us_only_blocks():
    a = assess(dict(BASE, description=BASE["description"] + " US only"), P)
    assert a["status"] == "BLOCKED"


def test_no_title_match_blocks():
    a = assess(dict(BASE, title="Customer Support"), P)
    assert a["status"] == "BLOCKED"


def test_salary_can_block_when_structured():
    p = dict(P, minimum_monthly_brl={"CLT": 4500})
    a = assess(dict(BASE, contract_type="CLT", salary_structured={"currency": "BRL", "interval": "month", "min": 4000}), p)
    assert a["status"] == "BLOCKED"


def test_usd_salary_not_assumed_brl():
    a = assess(dict(BASE, salary_structured={"currency": "USD", "interval": "month", "min": 10000}), P)
    assert a["salary_brl_monthly"] is None


def test_terms_are_word_bounded_and_accent_insensitive():
    assert includes_term("analista de automação", "automacao")
    assert not includes_term("bioinformatics", "informatics")
