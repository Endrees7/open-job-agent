from unittest.mock import Mock, patch
import pytest
from jobagent.providers import fetch_board


def test_greenhouse_read_only():
    response = Mock()
    response.json.return_value = {"jobs": [{"id":12,"title":"Integration Analyst", "location":{"name":"Remote Brazil"}, "absolute_url":"https://example.org/jobs/12", "content":"<b>Python</b> webhook"}]}
    with patch("jobagent.providers.requests.get", return_value=response) as get:
        rows = fetch_board({"provider":"greenhouse","slug":"sample","company":"Example"})
    assert rows[0]["id"] == "greenhouse:sample:12"
    assert "<b>" not in rows[0]["description"]
    assert get.call_args.args[0].startswith("https://boards-api.greenhouse.io/")


def test_lever_parsing():
    response = Mock()
    response.json.return_value = [{"id":"abc","text":"Automation Engineer", "categories":{"location":"Brazil"},"descriptionPlain":"Python", "hostedUrl":"https://example.org/a"}]
    with patch("jobagent.providers.requests.get", return_value=response):
        result = fetch_board({"provider":"lever", "slug":"sample"})
    assert len(result) == 1


def test_invalid_slug_rejected_before_network():
    with pytest.raises(ValueError):
        fetch_board({"provider":"lever","slug":"https://internal.example"})


def test_bad_provider_rejected():
    with pytest.raises(ValueError):
        fetch_board({"provider":"unknown","slug":"abc"})


def test_unlisted_ashby_filtered():
    response = Mock()
    response.json.return_value = {"jobs": [{"id":"x", "title":"X", "isListed":False,"jobUrl":"https://example.org/x"},
                                            {"id":"y", "title":"Y", "jobUrl":"https://example.org/y"}]}
    with patch("jobagent.providers.requests.get", return_value=response):
        result = fetch_board({"provider":"ashby", "slug":"sample"})
    assert len(result) == 1
