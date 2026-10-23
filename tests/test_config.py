import json
import pytest
from jobagent.config import ConfigurationError, load_private_profile, load_private_sources, load_demo_profile


def test_example_is_valid():
    assert load_demo_profile()["display_name"].startswith("Example")


def test_private_profile_only_from_secret(monkeypatch, tmp_path):
    p = load_demo_profile()
    p["display_name"] = "Private (never output)"
    monkeypatch.setenv("OJA_PROFILE_JSON", json.dumps(p))
    assert load_private_profile(str(tmp_path / "missing.json"))["display_name"].startswith("Private")


def test_invalid_json_does_not_echo_secret(monkeypatch, tmp_path):
    monkeypatch.setenv("OJA_PROFILE_JSON", "super-secret: invalid JSON")
    with pytest.raises(ConfigurationError) as exc:
        load_private_profile(str(tmp_path / "missing.json"))
    assert "super-secret" not in str(exc.value)


def test_sources_require_list(monkeypatch):
    monkeypatch.setenv("OJA_SOURCES_JSON", '{"boards": []}')
    with pytest.raises(ConfigurationError):
        load_private_sources()


def test_valid_sources(monkeypatch):
    monkeypatch.setenv("OJA_SOURCES_JSON", '{"boards": [{"provider":"lever", "slug":"sample"}]}')
    assert load_private_sources()["boards"][0]["provider"] == "lever"
