#!/usr/bin/env python3

"""Run the end-to-end Security Cloud Control example workflow."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scc_sdk_workflows.cisco_live_example import main


if __name__ == "__main__":
    raise SystemExit(main())
