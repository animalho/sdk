"""Step 1: list organizations through the Cisco Security Cloud Control SDK."""

from __future__ import annotations

from scc_sdk_workflows.client import create_client, print_json, run_with_error_handling


def main() -> int:
    def _run() -> None:
        client = create_client()
        response = client.organizations.list()
        print_json(response)

    return run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
