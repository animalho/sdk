# scc-sdk-workflows

Runnable Cisco Security Cloud Control SDK workflow examples for use alongside the learning lab.

## Setup

```bash
git clone https://github.com/animalho/sdk.git
cd sdk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set your environment variables:

```bash
export SCC_ORG_ID="your-organization-id"
export SCC_API_KEY_TOKEN="your-api-key-token"
export SCC_CLAIM_CODE="your-claim-code"
```

## Run the step scripts

Step 1, list organizations:

```bash
python3 scripts/01_list_orgs.py
```

Step 2, read claim code:

```bash
python3 scripts/02_read_claim_code.py
```

Step 3, organization setup workflow:

```bash
python3 scripts/03_setup_organization_flow.py
```

This example expects:

- `SCC_ORG_ID`
- `SCC_API_KEY_TOKEN`
- `SCC_CLAIM_CODE`
- optional `SCC_EXAMPLE_USERS_JSON`
- optional `SCC_EXAMPLE_GROUPS_JSON`
- optional `SCC_EXAMPLE_PRODUCT_FILTERS`

Example configuration:

```bash
export SCC_EXAMPLE_USERS_JSON='[
  {"email":"alice@example.com","firstName":"Alice","lastName":"Admin"},
  {"email":"bob@example.com","firstName":"Bob","lastName":"Operator"}
]'

export SCC_EXAMPLE_GROUPS_JSON='[
  {
    "name":"Lab Security Cloud Admins",
    "description":"Example admin group for the lab workflow",
    "users":["alice@example.com","bob@example.com"],
    "roles":[
      {
        "product":"Security Cloud Control",
        "displayName":"Organization Administrator"
      }
    ]
  }
]'
```

You can also run the example directly with `python3 examples/setup_organization_flow.py`.

Step 4, connect to the MCP agent:

```bash
export LLM_BASE_URL="your-llm-endpoint"
export LLM_API_KEY="your-llm-api-key"
python3 scripts/04_mcp_agent.py
```

Sample prompts:

```text
List my organizations
List my user roles in the organization
List the admin groups for the organization
```
