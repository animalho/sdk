#!/usr/bin/env python3

"""Run the end-to-end Security Cloud Control organization setup workflow."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts" / "03_setup_organization_flow.py"),
        run_name="__main__",
    )
