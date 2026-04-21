#!/usr/bin/env python3

"""Step 4: run the SCC MCP agent."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scc_sdk_workflows.mcp_agent import main


if __name__ == "__main__":
    raise SystemExit(main())
