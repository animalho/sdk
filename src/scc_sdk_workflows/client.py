"""Shared helpers for Cisco Security Cloud Control SDK scripts."""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def _require_sdk() -> tuple[Any, Any]:
    try:
        from scc_sdk import Client, SCCError
    except ImportError as exc:
        raise SystemExit(
            "The Cisco SCC SDK is not installed. Run "
            "`pip install -e .` or `pip install cisco-scc-sdk` first."
        ) from exc

    return Client, SCCError


def get_access_token() -> str:
    token = os.getenv("SCC_API_KEY_TOKEN")
    if not token:
        raise SystemExit(
            "Missing SCC API key token. Set `SCC_API_KEY_TOKEN` in your environment."
        )
    return token


def get_base_url() -> str:
    return os.getenv("SCC_BASE_URL", "https://api.security.cisco.com")


def create_client() -> Any:
    client_cls, _ = _require_sdk()
    return client_cls(
        access_token=get_access_token(),
        base_url=get_base_url(),
    )


def get_org_id() -> str:
    org_id = os.getenv("SCC_ORG_ID")
    if not org_id:
        raise SystemExit("Missing organization ID. Set `SCC_ORG_ID` in your environment.")
    return org_id


def get_claim_code() -> str:
    claim_code = os.getenv("SCC_CLAIM_CODE")
    if not claim_code:
        raise SystemExit("Missing claim code. Set `SCC_CLAIM_CODE` in your environment.")
    return claim_code


def get_scc_error_type() -> Any:
    _, scc_error = _require_sdk()
    return scc_error


def print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def exit_with_error(exc: Exception) -> "NoReturn":
    details = {"error": str(exc)}
    for attr, key in (
        ("message", "message"),
        ("status_code", "statusCode"),
        ("tracking_id", "trackingId"),
        ("timestamp", "timestamp"),
        ("path", "path"),
    ):
        value = getattr(exc, attr, None)
        if value:
            details[key] = value

    print_json(details)
    raise SystemExit(1) from exc


def run_with_error_handling(callback: Any) -> int:
    scc_error = get_scc_error_type()
    try:
        callback()
        return 0
    except scc_error as exc:
        exit_with_error(exc)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
