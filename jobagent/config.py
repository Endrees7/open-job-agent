"""Private runtime configuration, intentionally not stored in Git."""
from __future__ import annotations
import json
import os
from pathlib import Path


class ConfigurationError(ValueError):
    """Configuration missing or invalid (without including private content)."""


def _load(kind: str, private_path: str) -> dict:
    env_key = f"OJA_{kind.upper()}_JSON"
    raw = os.environ.get(env_key)
    try:
        if raw is None:
            path = Path(private_path)
            if not path.is_file():
                raise ConfigurationError(f"Missing {kind} configuration: set {env_key} or create {private_path}")
            raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise ConfigurationError(f"Invalid {kind} JSON (content hidden)") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Invalid {kind}: expected a JSON object")
    return data


def validate_profile(p: dict) -> dict:
    terms = p.get("priority_terms")
    skills = p.get("confirmed_skills")
    if not isinstance(terms, list) or not terms or not all(isinstance(x, str) and 2 <= len(x) <= 80 for x in terms):
        raise ConfigurationError("priority_terms must be a non-empty list of text")
    if not isinstance(skills, list) or not all(isinstance(x, str) and 1 <= len(x) <= 80 for x in skills):
        raise ConfigurationError("confirmed_skills must be a list of text")
    if p.get("preferred_workplace", "remote") not in ("remote", "any"):
        raise ConfigurationError("preferred_workplace must be remote or any")
    for key, low, high in (("review_score_threshold", 0, 100), ("max_jobs_per_run", 1, 60), ("max_boards_per_run", 1, 15)):
        v = p.get(key)
        if type(v) is not int or not low <= v <= high:
            raise ConfigurationError(f"{key} must be an integer in [{low}, {high}]")
    country = p.get("country_keywords", [])
    if not isinstance(country, list) or not all(isinstance(x, str) and x for x in country):
        raise ConfigurationError("country_keywords must be a list")
    salary = p.get("minimum_monthly_brl", {})
    if not isinstance(salary, dict) or any(type(v) not in (float, int, type(None)) or (v is not None and v < 0) for v in salary.values()):
        raise ConfigurationError("minimum_monthly_brl must have non-negative numeric values or null")
    return p


def validate_sources(src: dict) -> dict:
    boards = src.get("boards")
    if not isinstance(boards, list) or not boards:
        raise ConfigurationError("No job boards configured: add public board slugs privately")
    if len(boards) > 30 or any(not isinstance(x, dict) or x.get("provider") not in ("lever", "greenhouse", "ashby") for x in boards):
        raise ConfigurationError("boards must be a list of supported provider objects")
    return src


def load_private_profile(path: str = "config/private/profile.json") -> dict:
    return validate_profile(_load("profile", path))


def load_private_sources(path: str = "config/private/sources.json") -> dict:
    return validate_sources(_load("sources", path))


def load_demo_profile() -> dict:
    path = Path(__file__).resolve().parents[1] / "config/profile.example.json"
    return validate_profile(json.loads(path.read_text(encoding="utf-8")))
