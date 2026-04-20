#!/usr/bin/env python3

"""Step 3: validate and claim SCC subscriptions."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scc_sdk_workflows.claim_subscription import main


if __name__ == "__main__":
    raise SystemExit(main())
