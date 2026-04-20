"""Connectivity check for the Cisco Security Cloud Control SDK."""

from __future__ import annotations

import argparse

from scc_sdk_workflows.client import create_client, print_json, run_with_error_handling


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an SCC SDK client and optionally fetch organizations."
    )
    parser.add_argument(
        "--skip-api-call",
        action="store_true",
        help="Only validate that the SDK can be initialized with the configured token.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    def _run() -> None:
        client = create_client()
        if args.skip_api_call:
            print_json(
                {
                    "connected": True,
                    "message": "SDK client initialized successfully.",
                }
            )
            return

        organizations = client.organizations.list()
        items = organizations.get("items", []) if isinstance(organizations, dict) else []
        print_json(
            {
                "connected": True,
                "message": "SDK client initialized and organizations retrieved successfully.",
                "organizationCount": len(items),
                "organizations": organizations,
            }
        )

    return run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
