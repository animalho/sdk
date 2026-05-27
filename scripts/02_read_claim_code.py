#!/usr/bin/env python3

"""Step 2: read SCC claim code details."""

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


def _get_access_token() -> str:
    token = os.getenv("SCC_API_KEY_TOKEN")
    if not token:
        raise SystemExit(
            "Missing SCC API key token. Set `SCC_API_KEY_TOKEN` in your environment."
        )
    return token


def _get_org_id() -> str:
    org_id = os.getenv("SCC_ORG_ID")
    if not org_id:
        raise SystemExit("Missing organization ID. Set `SCC_ORG_ID` in your environment.")
    return org_id


def _get_claim_code() -> str:
    claim_code = os.getenv("SCC_CLAIM_CODE")
    if not claim_code:
        raise SystemExit("Missing claim code. Set `SCC_CLAIM_CODE` in your environment.")
    return claim_code


def _create_client() -> Any:
    client_cls, _ = _require_sdk()
    return client_cls(
        access_token=_get_access_token(),
        base_url=os.getenv("SCC_BASE_URL", "https://api.security.cisco.com"),
    )


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _exit_with_error(exc: Exception) -> "NoReturn":
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

    _print_json(details)
    raise SystemExit(1) from exc


def main() -> int:
    _, scc_error = _require_sdk()
    try:
        response = _create_client().subscriptions.read_claim_code(
            org_id=_get_org_id(),
            claim_code=_get_claim_code(),
        )
        _print_json(response)
        return 0
    except scc_error as exc:
        _exit_with_error(exc)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
