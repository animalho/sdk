"""Step 3: placeholder for a multi-step guided workflow."""

from __future__ import annotations

from scc_sdk_workflows.client import get_claim_code, get_org_id, print_json


def main() -> int:
    print_json(
        {
            "implemented": False,
            "message": "This step is a placeholder for a future one-click workflow.",
            "plannedSteps": [
                "Validate the organization and API key token",
                "List organizations and subscriptions",
                "Read claim code details",
                "Guide follow-up actions based on the claim information",
            ],
            "context": {
                "orgId": get_org_id(),
                "claimCode": get_claim_code(),
            },
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
