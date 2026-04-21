"""Step 2: read claim code details through the Cisco Security Cloud Control SDK."""

from __future__ import annotations

from scc_sdk_workflows.client import (
    create_client,
    get_claim_code,
    get_org_id,
    print_json,
    run_with_error_handling,
)


def main() -> int:
    def _run() -> None:
        client = create_client()
        response = client.subscriptions.read_claim_code(
            org_id=get_org_id(),
            claim_code=get_claim_code(),
        )
        print_json(response)

    return run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
