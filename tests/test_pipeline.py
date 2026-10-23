import json
from unittest.mock import patch
from jobagent.config import load_demo_profile
from jobagent.pipeline import assemble, scan
from jobagent.cli import main


def test_demo_offline(tmp_path):
    path = tmp_path / "report.json"
    assert main(["demo", "--output", str(path)]) == 0
    result = json.loads(path.read_text())
    assert result["source"] == "synthetic_demo"
    assert len(result["jobs"]) == 3
    assert all(x["auto_apply"] is False for x in result["jobs"])


def test_duplicate_jobs_not_repeated():
    rows = [{"id":"demo:a", "url":"https://example.org/a", "title":"Automation Engineer", "description":"Python", "company":"Example", "location":"Brazil"}] * 3
    r = assemble(rows, load_demo_profile(), "demo")
    assert r["stats"]["deduplicated"] == 1


def test_scan_provider_error_isolated():
    sources = {"boards": [{"provider":"lever", "slug":"example"}, {"provider":"greenhouse", "slug":"test"}]}
    with patch("jobagent.pipeline.fetch_board", side_effect=[RuntimeError("do not print this"), []]):
        report = scan(sources, load_demo_profile())
    assert report["stats"]["errors"] == 1
    assert report["jobs"] == []


def test_test_webhook_does_not_require_secrets(tmp_path):
    assert main(["test-webhook", "--output", str(tmp_path / "report.json")]) == 0


def test_scan_missing_private_config_fails_closed(tmp_path, monkeypatch):
    monkeypatch.delenv("OJA_PROFILE_JSON", raising=False)
    monkeypatch.delenv("OJA_SOURCES_JSON", raising=False)
    monkeypatch.chdir(tmp_path)
    assert main(["scan", "--output", "output.json"]) == 2
    assert not (tmp_path / "output.json").exists()
