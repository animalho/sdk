"""Claim an SCC subscription by claim code using the SDK."""

from __future__ import annotations

import argparse
from typing import Any

from scc_sdk_workflows.client import create_client, print_json, run_with_error_handling


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a claim code and optionally create a subscription."
    )
    parser.add_argument("--org-id", required=True, help="Target organization ID.")
    parser.add_argument("--claim-code", required=True, help="Subscription claim code.")
    parser.add_argument(
        "--preferred-region",
        help="Preferred region to use when building products from claim info.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the claim code and print claim details without creating a subscription.",
    )
    return parser


def _build_products(client: Any, claim_info: dict[str, Any], preferred_region: str | None) -> Any:
    builder = getattr(client.subscriptions, "build_products_from_claim_info", None)
    if builder is None:
        return None
    if preferred_region:
        return builder(claim_info, preferred_region=preferred_region)
    return builder(claim_info)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    def _run() -> None:
        client = create_client()

        claim_info = client.subscriptions.read_claim_code(
            org_id=args.org_id,
            claim_code=args.claim_code,
        )

        if args.dry_run:
            print_json(
                {
                    "validated": True,
                    "created": False,
                    "claimInfo": claim_info,
                }
            )
            return

        products = _build_products(client, claim_info, args.preferred_region)
        create_kwargs = {
            "org_id": args.org_id,
            "claim_code": args.claim_code,
        }
        if products is not None:
            create_kwargs["products"] = products

        result = client.subscriptions.create(**create_kwargs)
        print_json(
            {
                "validated": True,
                "created": True,
                "claimInfo": claim_info,
                "subscription": result,
            }
        )

    return run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
