#!/usr/bin/env python3

"""Step 3: run the organization setup workflow."""

from __future__ import annotations

import json
import os
import sys
from typing import Any


DEFAULT_PRODUCT_FILTERS = ("Secure Access", "Firewall")
DEFAULT_USERS = [
    {
        "email": "member1@cl-workshop.com",
        "firstName": "Member",
        "lastName": "Ciscolive",
    },
    {
        "email": "member2@cl-workshop.com",
        "firstName": "member2",
        "lastName": "Ciscolive",
    },
]

DEFAULT_GROUPS = [
    {
        "name": "Lab Security Cloud Admins",
        "description": "Example admin group for the lab workflow",
        "roles": [
            {
                "product": "Secure Access",
                "displayName": "Security Admin",
            }
        ],
    }
]


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


def _run_with_error_handling(callback: Any) -> int:
    _, scc_error = _require_sdk()
    try:
        callback()
        return 0
    except scc_error as exc:
        _exit_with_error(exc)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130


def _load_json_env(var_name: str, default: Any) -> Any:
    raw_value = os.getenv(var_name)
    if not raw_value:
        return default

    try:
        return json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Invalid JSON in {var_name}. Provide valid JSON. Error: {exc.msg}"
        ) from exc


def _load_users() -> list[dict[str, str]]:
    return _load_json_env("SCC_EXAMPLE_USERS_JSON", DEFAULT_USERS)


def _load_groups() -> list[dict[str, Any]]:
    groups = _load_json_env("SCC_EXAMPLE_GROUPS_JSON", DEFAULT_GROUPS)

    users = _load_users()
    user_emails = [user["email"] for user in users if "email" in user]
    for group in groups:
        group.setdefault("users", list(user_emails))
        group.setdefault("roles", [])

    return groups


def _load_product_filters() -> list[str]:
    raw_value = os.getenv("SCC_EXAMPLE_PRODUCT_FILTERS")
    if not raw_value:
        return list(DEFAULT_PRODUCT_FILTERS)

    filters = [item.strip() for item in raw_value.split(",") if item.strip()]
    return filters or list(DEFAULT_PRODUCT_FILTERS)


def _select_products(
    claim_info: dict[str, Any], preferred_region: str, product_filters: list[str]
) -> list[dict[str, Any]]:
    selected_products: list[dict[str, Any]] = []
    normalized_filters = [value.casefold() for value in product_filters]

    for product in claim_info.get("products", []):
        name = str(product.get("name", ""))
        if normalized_filters and not any(
            filter_value in name.casefold() for filter_value in normalized_filters
        ):
            continue

        allowed_regions = product.get("allowedRegions", [])
        selected_region = next(
            (
                region
                for region in allowed_regions
                if region.get("regionCode") == preferred_region
            ),
            allowed_regions[0] if allowed_regions else None,
        )
        if not selected_region:
            continue

        selected_products.append(
            {
                "id": product.get("id"),
                "name": name,
                "useExistingTenant": False,
                "regionCode": selected_region.get("regionCode"),
                "regionDescription": selected_region.get("regionDescription"),
            }
        )

    return selected_products


def _find_group(groups_result: dict[str, Any], name: str) -> dict[str, Any] | None:
    for group in groups_result.get("groups", []):
        if group.get("name") == name:
            return group
    return None


def _print_organization_details(organization: dict[str, Any]) -> None:
    print("\n✓ Organization Details:")
    print(f"  - Name: {organization.get('name')}")
    print(f"  - Type: {organization.get('type')}")
    print(
        "  - Region: "
        f"{organization.get('regionCode')} - {organization.get('regionDescription')}"
    )
    print(f"  - Created: {organization.get('created')}")


def _print_user_patch_results(patch_result: dict[str, Any]) -> None:
    results = patch_result.get("results", [])
    if not results:
        print("  - No user invite results returned.")
        return

    for result in results:
        email = result.get("email", "unknown")
        status = result.get("status", "unknown")
        print(f"  - {email}: {status}")
        if result.get("errorDescription"):
            print(f"    Error: {result['errorDescription']}")


def _find_role_id(
    roles_result: dict[str, Any], product_name: str, role_display_name: str
) -> str | None:
    for role in roles_result.get("roles", []):
        product_names = [
            product.get("name")
            for product in role.get("products", [])
            if isinstance(product, dict)
        ]
        if (
            role.get("displayName") == role_display_name
            and product_name in product_names
        ):
            return role.get("id")
    return None


def _invite_users(
    client: Any, org_id: str, users: list[dict[str, str]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not users:
        print("Skipping user invitations: no SCC_EXAMPLE_USERS_JSON provided.")
        return results

    print("\nStep 3: Inviting users")
    patch_result = client.users.patch(
        org_id=org_id,
        users=[
            {
                "email": user["email"],
                "operation": "invite",
                "firstName": user["firstName"],
                "lastName": user["lastName"],
            }
            for user in users
        ],
    )
    _print_user_patch_results(patch_result)
    results.extend(patch_result.get("results", []))
    return results


def _create_or_get_groups(
    client: Any, org_id: str, groups: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    created_groups: list[dict[str, Any]] = []

    if not groups:
        print("Skipping admin groups: no SCC_EXAMPLE_GROUPS_JSON provided.")
        return created_groups

    print("\nStep 4: Creating admin groups")
    existing_groups = client.groups.list(org_id=org_id)
    for group in groups:
        existing = _find_group(existing_groups, group["name"])
        if existing:
            print(f"  - Reusing existing group: {group['name']}")
            created_groups.append(existing)
            continue

        created = client.groups.create(
            org_id=org_id,
            name=group["name"],
            description=group.get("description"),
        )
        print(f"  - Created group: {created.get('name')} ({created.get('id')})")
        created_groups.append(created)

    return created_groups


def _assign_users_to_groups(
    client: Any,
    org_id: str,
    groups: list[dict[str, Any]],
    created_groups: list[dict[str, Any]],
) -> None:
    group_by_name = {group["name"]: group for group in created_groups}

    for group in groups:
        group_name = group["name"]
        users = group.get("users", [])
        if not users:
            continue

        created_group = group_by_name.get(group_name)
        if not created_group:
            continue

        client.groups.patch(
            org_id=org_id,
            group_id=created_group["id"],
            users=[{"operation": "add", "id": user_email} for user_email in users],
        )
        print(f"  - Added {len(users)} user(s) to group: {group_name}")


def _assign_roles_to_groups(
    client: Any,
    org_id: str,
    groups: list[dict[str, Any]],
    created_groups: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    print("\nStep 5: Assigning roles to groups")
    assignment_results: list[dict[str, Any]] = []
    group_by_name = {group["name"]: group for group in created_groups}
    roles_result = client.roles.list(org_id=org_id)

    for group in groups:
        created_group = group_by_name.get(group["name"])
        if not created_group:
            continue

        for role in group.get("roles", []):
            role_id = _find_role_id(
                roles_result=roles_result,
                product_name=role["product"],
                role_display_name=role["displayName"],
            )
            if not role_id:
                print(
                    "  - Skipping role assignment because the role was not found: "
                    f"{role['product']} / {role['displayName']}"
                )
                assignment_results.append(
                    {
                        "group": group["name"],
                        "role": role,
                        "status": "not_found",
                    }
                )
                continue

            result = client.roles.patch(
                org_id=org_id,
                role_id=role_id,
                groups=[{"operation": "add", "id": created_group["id"]}],
            )
            summary = result.get("summary", {})
            print(
                f"  - Assigned {role['displayName']} to {group['name']} "
                f"(success={summary.get('success', 0)}, failed={summary.get('failed', 0)})"
            )
            assignment_results.append(
                {
                    "group": group["name"],
                    "role": role,
                    "result": result,
                }
            )

    return assignment_results


def _run() -> None:
    client = _create_client()
    org_id = _get_org_id()
    claim_code = _get_claim_code()
    preferred_region = os.getenv("SCC_EXAMPLE_REGION", "NAM")
    product_filters = _load_product_filters()
    users = _load_users()
    groups = _load_groups()

    print("Step 1: Getting organization details")
    organization = client.organizations.get(org_id=org_id)
    _print_organization_details(organization)

    print("\nStep 2: Claiming subscriptions")
    claim_info = client.subscriptions.read_claim_code(
        org_id=org_id, claim_code=claim_code
    )
    selected_products = _select_products(
        claim_info=claim_info,
        preferred_region=preferred_region,
        product_filters=product_filters,
    )
    if not selected_products:
        raise SystemExit(
            "No products matched the configured claim filters. "
            "Set SCC_EXAMPLE_PRODUCT_FILTERS to match the claim code products."
        )

    subscription_result = client.subscriptions.create(
        org_id=org_id,
        claim_code=claim_code,
        products=[
            {
                "id": product["id"],
                "useExistingTenant": product["useExistingTenant"],
                "regionCode": product["regionCode"],
                "regionDescription": product["regionDescription"],
            }
            for product in selected_products
        ],
    )
    print(
        "  - Submitted claim for products: "
        + ", ".join(product["name"] for product in selected_products)
    )

    invited_users = _invite_users(client=client, org_id=org_id, users=users)
    created_groups = _create_or_get_groups(client=client, org_id=org_id, groups=groups)
    _assign_users_to_groups(
        client=client,
        org_id=org_id,
        groups=groups,
        created_groups=created_groups,
    )
    role_assignments = _assign_roles_to_groups(
        client=client,
        org_id=org_id,
        groups=groups,
        created_groups=created_groups,
    )

    print("\nWorkflow summary")
    _print_json(
        {
            "organization": {
                "id": organization.get("id", org_id),
                "name": organization.get("name"),
                "type": organization.get("type"),
            },
            "claimedProducts": selected_products,
            "subscriptionResult": subscription_result,
            "invitedUsers": invited_users,
            "groups": created_groups,
            "roleAssignments": role_assignments,
        }
    )


def main() -> int:
    return _run_with_error_handling(_run)


if __name__ == "__main__":
    raise SystemExit(main())
