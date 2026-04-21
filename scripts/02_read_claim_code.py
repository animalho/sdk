#!/usr/bin/env python3

"""Step 2: read SCC claim code details."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scc_sdk_workflows.read_claim_code import main


if __name__ == "__main__":
    raise SystemExit(main())
