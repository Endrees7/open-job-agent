"""Read-only adapters for official employer public job-board APIs."""
from __future__ import annotations
import html
import re
from urllib.parse import quote
import requests


def plain_text(value: object) -> str:
    raw = str(value or "")
    raw = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw)
    raw = re.sub(r"<[^>]*>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def fetch_board(board: dict, timeout: int = 15) -> list[dict]:
    provider = board.get("provider", "")
    slug = board.get("slug", "")
    if not isinstance(slug, str) or not re.fullmatch(r"[A-Za-z0-9_-]{2,65}", slug):
        raise ValueError("Invalid public board slug")
    if provider == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{quote(slug)}/jobs"
        params = {"content": "true"}
    elif provider == "lever":
        url = f"https://api.lever.co/v0/postings/{quote(slug)}"
        params = {"mode": "json"}
    elif provider == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{quote(slug)}"
        params = {"includeCompensation": "true"}
    else:
        raise ValueError("Unsupported read-only provider")
    response = requests.get(url, params=params, timeout=timeout,
                            headers={"User-Agent": "OpenJobAgent/0.1 (read-only career research)", "Accept": "application/json"})
    response.raise_for_status()
    data = response.json()
    raw = data if provider == "lever" else data.get("jobs", [])
    if not isinstance(raw, list):
        raise ValueError("Provider response has no jobs list")
    result = []
    for j in raw[:300]:
        try:
            if provider == "greenhouse":
                job_id = str(j["id"])
                title = j["title"]
                location = (j.get("location") or {}).get("name", "")
                desc = j.get("content", "")
                link = j["absolute_url"]
                salary = {}
            elif provider == "lever":
                job_id = str(j["id"])
                title = j["text"]
                location = (j.get("categories") or {}).get("location", "")
                desc = j.get("descriptionPlain") or j.get("description") or ""
                link = j.get("hostedUrl") or j.get("applyUrl") or ""
                salary = j.get("salaryRange") or {}
            else:
                if j.get("isListed") is False:
                    continue
                job_id = str(j.get("id") or "")
                title = j["title"]
                location = j.get("location", "")
                desc = j.get("descriptionPlain") or j.get("descriptionHtml") or ""
                link = j.get("jobUrl") or j.get("applyUrl") or ""
                salary = j.get("compensation") or {}
            if not job_id or not title or not isinstance(link, str) or not link.startswith("https://"):
                continue
            result.append({
                "id": f"{provider}:{slug}:{job_id}", "provider": provider,
                "company": plain_text(board.get("company") or slug),
                "title": plain_text(title), "location": plain_text(location),
                "workplace_type": plain_text(j.get("workplaceType", "")),
                "description": plain_text(desc)[:2500], "url": link[:500],
                "salary_structured": salary, "contract_type": "UNKNOWN"
            })
        except (KeyError, TypeError, AttributeError):
            continue
    return result
