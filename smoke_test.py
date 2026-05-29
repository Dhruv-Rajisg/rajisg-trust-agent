#!/usr/bin/env python3
"""Smoke test RPCA agent tools against live validator (no Gemini required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))

from rpca_compliance_agent.tools import (  # noqa: E402
    export_compliance_evidence,
    get_policy_controls,
    validate_content_credentials,
)


def _sample_file() -> Path:
    candidates = [
        ROOT / "local-preview" / "conformance-screenshots" / "T2I_Puppy.png",
        ROOT / "local-preview" / "conformance-screenshots" / "_test-puppy.png",
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise SystemExit("No sample image found under local-preview/conformance-screenshots/")


def main() -> None:
    sample = _sample_file()
    print(f"Sample: {sample}")
    v = validate_content_credentials(str(sample))
    print("validate:", v.get("status"), v.get("validation_status_public"))
    if v.get("status") != "success":
        print(v)
        raise SystemExit(1)
    p = get_policy_controls("both")
    print("policy controls:", len(p.get("controls", [])))
    e = export_compliance_evidence(
        filename=v.get("filename") or sample.name,
        validation_status_public=v.get("validation_status_public") or "Unknown",
        jurisdiction="both",
        headline=v.get("headline") or "",
        subhead=v.get("subhead") or "",
        use_case="hackathon_smoke_test",
    )
    print("evidence:", e.get("evidence_path"))
    print("OK")


if __name__ == "__main__":
    main()
