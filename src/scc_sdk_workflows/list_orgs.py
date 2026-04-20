"""List organizations through the Cisco Security Cloud Control SDK."""

from __future__ import annotations

import argparse

from scc_sdk_workflows.client import create_client, print_json, run_with_error_handling


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="List Security Cloud Control organizations.")
    parser.add_argument("--name", help="Optional partial organization name filter.")
    parser.add_argument(
        "--type",
        dest="org_type",
        help="Optional organization type filter, for example STANDALONE or MANAGER.",
    )
    parser.add_argument(
        "--region-code",
        help="Optional region filter, for example NAM, EMEA, APJC, or GLOBAL.",
    )
    parser.add_argument(
        "--country-code",
        help="Optional country code filter.",
    )
    parser.add_argument(
        "--manager-org-id",
        help="Optional manager organization ID filter.",
    )
    parser.add_argument(
        "--max",
        dest="max_items",
        type=int,
        default=100,
        help="Maximum number of organizations to return.",
    )
    parser.add_argument("--cursor", help="Pagination cursor.")
    parser.add_argument("--sort-by", help="Field to sort by.")
    parser.add_argument("--order", help="Sort order, typically ASC or DESC.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    def _run() -> None:
        client = create_client()
        response = client.organizations.list(
            name=args.name,
            type=args.org_type,
            region_code=args.region_code,
            country_code=args.country_code,
            manager_org_id=args.manager_org_id,
            max=args.max_items,
            cursor=args.cursor,
            sort_by=args.sort_by,
            order=args.order,
        )
        print_json(response)

    return run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
