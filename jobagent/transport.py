"""HMAC-signed transport; no credentials in committed files or normal logs."""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from urllib.parse import urlsplit
import requests


def envelope(payload: dict, secret: str, *, timestamp: int | None = None, nonce: str | None = None) -> dict:
    if len(secret) < 32:
        raise ValueError("OJA_HMAC_SECRET must contain at least 32 characters")
    ts = int(time.time()) if timestamp is None else int(timestamp)
    n = secrets.token_hex(16) if nonce is None else nonce
    if len(n) != 32 or any(c not in '0123456789abcdef' for c in n):
        raise ValueError("Invalid nonce")
    body = base64.b64encode(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii")
    sig = hmac.new(secret.encode("utf-8"), f"{ts}.{n}.{body}".encode("utf-8"), hashlib.sha256).hexdigest()
    return {"timestamp": ts, "nonce": n, "payload_b64": body, "signature": sig}


def send_report(report: dict) -> dict:
    endpoint = os.getenv("OJA_APPS_SCRIPT_URL", "")
    secret = os.getenv("OJA_HMAC_SECRET", "")
    parsed = urlsplit(endpoint)
    if parsed.scheme != "https" or parsed.hostname != "script.google.com" or not parsed.path.startswith("/macros/s/") or not parsed.path.endswith("/exec") or parsed.username or parsed.password:
        raise ValueError("Missing or invalid Apps Script /exec URL")
    request = envelope(report, secret)
    response = requests.post(endpoint, json=request, timeout=70)
    response.raise_for_status()
    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Apps Script did not return JSON") from exc
    if not isinstance(data, dict) or not data.get("ok"):
        raise RuntimeError("Apps Script rejected report; inspect the private Apps Script execution logs")
    return {"inserted": int(data.get("inserted", 0)), "updated": int(data.get("updated", 0))}
