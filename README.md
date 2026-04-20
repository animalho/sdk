# scc-sdk-workflows

Runnable Cisco Security Cloud Control SDK workflow examples for use alongside the learning lab.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set your access token:

```bash
export SCC_ACCESS_TOKEN="your-security-cloud-control-access-token"
```

## Run the step scripts

Step 1, connect to the SDK:

```bash
python3 scripts/01_connect_sdk.py
```

Step 2, list organizations:

```bash
python3 scripts/02_list_orgs.py
```

Step 3, validate a claim code:

```bash
python3 scripts/03_claim_subscription.py --org-id <org-id> --claim-code <claim-code> --dry-run
```

Step 3, claim a subscription:

```bash
python3 scripts/03_claim_subscription.py --org-id <org-id> --claim-code <claim-code> --preferred-region NAM
```
