"""Gather, deduplicate, evaluate, and prepare a limited-size report."""
from __future__ import annotations
from .providers import fetch_board
from .scoring import assess


def assemble(jobs: list[dict], profile: dict, source: str) -> dict:
    unique: dict[str, dict] = {}
    for row in jobs:
        if not isinstance(row, dict) or not row.get("id") or not row.get("title") or not str(row.get("url", "")).startswith("https://"):
            continue
        key = str(row["id"])[:180]
        if key in unique:
            continue
        clean = {"id": key, "provider": str(row.get("provider", ""))[:40],
                 "company": str(row.get("company", ""))[:160], "title": str(row["title"])[:250],
                 "location": str(row.get("location", ""))[:150],
                 "workplace_type": str(row.get("workplace_type", ""))[:40],
                 "description": str(row.get("description", ""))[:1300],
                 "url": str(row["url"])[:500], "contract_type": str(row.get("contract_type", "UNKNOWN"))[:20]}
        assessment = assess(row, profile)
        # Do not export private candidate profile or the entire raw job description.
        clean.update(assessment)
        unique[key] = clean
    ranked = sorted(unique.values(), key=lambda j: (-j["score"], j["id"]))[:profile["max_jobs_per_run"]]
    return {"schema_version": 1, "source": source, "jobs": ranked,
            "stats": {"seen": len(jobs), "deduplicated": len(unique), "reported": len(ranked),
                      "review": sum(j["status"] == "REVIEW" for j in ranked), "errors": 0}}


def scan(sources: dict, profile: dict) -> dict:
    all_jobs = []
    error_boards = 0
    for board in sources["boards"][:profile["max_boards_per_run"]]:
        try:
            all_jobs.extend(fetch_board(board))
        except Exception:  # noqa: BLE001: isolate provider failures; never print unsafe URLs/responses
            error_boards += 1
    report = assemble(all_jobs, profile, "official_public_boards")
    report["stats"]["errors"] = error_boards
    return report
