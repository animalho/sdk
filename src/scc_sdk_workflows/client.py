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
    token = os.getenv("SCC_ACCESS_TOKEN") or os.getenv("SCC_API_KEY")
    if not token:
        raise SystemExit(
            "Missing SCC access token. Set `SCC_ACCESS_TOKEN` "
            "(or `SCC_API_KEY`) in your environment."
        )
    return token


def create_client() -> Any:
    client_cls, _ = _require_sdk()
    return client_cls(access_token=get_access_token())


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
