import base64
import hashlib
import hmac
import json
from unittest.mock import Mock, patch
import pytest
from jobagent.transport import envelope, send_report


def test_signed_envelope_is_deterministic():
    content = {"schema_version": 1, "jobs": []}
    msg = envelope(content, "A"*40, timestamp=1730000000, nonce="a"*32)
    expected = hmac.new(b"A"*40, f"1730000000.{msg['nonce']}.{msg['payload_b64']}".encode(), hashlib.sha256).hexdigest()
    assert msg["signature"] == expected
    assert json.loads(base64.b64decode(msg["payload_b64"])) == content


def test_short_secret_rejected():
    with pytest.raises(ValueError):
        envelope({}, "weak")


def test_external_endpoint_rejected(monkeypatch):
    monkeypatch.setenv("OJA_APPS_SCRIPT_URL", "https://example.org/hook")
    monkeypatch.setenv("OJA_HMAC_SECRET", "A"*40)
    with pytest.raises(ValueError):
        send_report({"schema_version":1,"jobs":[]})


def test_safe_sync_response(monkeypatch):
    monkeypatch.setenv("OJA_APPS_SCRIPT_URL", "https://script.google.com/macros/s/sample/exec")
    monkeypatch.setenv("OJA_HMAC_SECRET", "A"*40)
    resp = Mock()
    resp.json.return_value = {"ok":True,"inserted":2,"updated":1}
    with patch("jobagent.transport.requests.post", return_value=resp) as post:
        ack = send_report({"schema_version":1,"jobs":[]})
    assert ack == {"inserted":2,"updated":1}
    assert "OJA_HMAC_SECRET" not in repr(post.call_args)
