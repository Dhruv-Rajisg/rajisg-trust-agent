"""ADK tools — call live RPCA validate API + export evidence packs."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .policy import get_controls, recommend_disclosures

_DEFAULT_VALIDATE_URL = (
    "https://contentauthenticity.rajisg.com/contentauthenticity/v1/validate?technical=1"
)
_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def _validate_url() -> str:
    return os.environ.get("RPCA_VALIDATE_URL", "").strip() or _DEFAULT_VALIDATE_URL


def validate_content_credentials(local_file_path: str) -> dict:
    """Validate a local media file with the live RajISG RPCA validator (C2PA).

    Args:
        local_file_path: Absolute or relative path to jpeg/png/webp/mp4/pdf etc.

    Returns:
        Summary dict with validation_status_public, display headline, and key signals.
    """
    path = Path(local_file_path).expanduser().resolve()
    if not path.is_file():
        return {"status": "error", "message": f"File not found: {path}"}

    mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".mp4": "video/mp4",
        ".wav": "audio/wav",
        ".pdf": "application/pdf",
    }.get(path.suffix.lower(), "application/octet-stream")

    try:
        with path.open("rb") as fh:
            resp = requests.post(
                _validate_url(),
                files={"file": (path.name, fh, mime)},
                timeout=120,
            )
    except requests.RequestException as exc:
        return {"status": "error", "message": f"Validate request failed: {exc}"}

    if resp.status_code != 200:
        return {
            "status": "error",
            "http_status": resp.status_code,
            "message": resp.text[:2000],
        }

    try:
        payload = resp.json()
    except json.JSONDecodeError:
        return {"status": "error", "message": "Validator returned non-JSON response"}

    display = payload.get("display") if isinstance(payload.get("display"), dict) else {}
    conformant = payload.get("conformant_product_match") or {}
    return {
        "status": "success",
        "filename": payload.get("filename") or path.name,
        "validation_status_public": payload.get("validation_status_public"),
        "c2pa_validation_state": payload.get("c2pa_validation_state"),
        "headline": display.get("headline"),
        "subhead": display.get("subhead"),
        "validation_ok": payload.get("validation_ok"),
        "conformant_product": conformant.get("label") if isinstance(conformant, dict) else None,
        "issuer_hint": _issuer_hint(payload),
        "engine": "RajISG RPCA Validator (live Cloud Run)",
    }


def _issuer_hint(payload: Dict[str, Any]) -> Optional[str]:
    technical = payload.get("technical")
    if not isinstance(technical, dict):
        return None
    raw = technical.get("raw_json")
    if not isinstance(raw, dict):
        return None
    for block in raw.get("validation_results") or []:
        if not isinstance(block, dict):
            continue
        for expl in block.get("explanations") or []:
            if not isinstance(expl, dict):
                continue
            code = str(expl.get("code") or "")
            if "signingCredential" in code or "certificate" in code.lower():
                return str(expl.get("message") or "")[:500]
    return None


def get_policy_controls(jurisdiction: str = "both") -> dict:
    """Return EU Art. 50 and/or India IT Rules control checklist for compliance mapping.

    Args:
        jurisdiction: One of eu, india, both, global.
    """
    return {"status": "success", **get_controls(jurisdiction)}


def export_compliance_evidence(
    *,
    filename: str,
    validation_status_public: str,
    jurisdiction: str = "both",
    headline: str = "",
    subhead: str = "",
    use_case: str = "publication",
    notes: str = "",
) -> dict:
    """Write an audit-ready compliance evidence pack JSON to agent/output/.

    Args:
        filename: Original asset name.
        validation_status_public: Trusted / Valid / Unrecognized / Invalid / etc.
        jurisdiction: eu, india, both, or global.
        headline: Validator display headline.
        subhead: Validator display subhead.
        use_case: e.g. newsroom, ai_studio, cyber_triage.
        notes: Optional agent notes for the pack.
    """
    run_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    disclosures = recommend_disclosures(
        validation_status_public=validation_status_public,
        jurisdiction=jurisdiction,
    )
    pack = {
        "run_id": run_id,
        "generated_at_utc": ts,
        "product": "RPCA Compliance Agent",
        "operator": "RajISG Provenance & Content Authenticity",
        "use_case": use_case,
        "asset": {"filename": filename},
        "validation": {
            "validation_status_public": validation_status_public,
            "headline": headline,
            "subhead": subhead,
        },
        "policy": get_controls(jurisdiction),
        "recommended_disclosures": disclosures,
        "agent_notes": notes,
        "truth_label": (
            "This pack records cryptographic validation outcomes and suggested controls. "
            "It does not certify editorial truth or legal compliance."
        ),
    }
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _OUTPUT_DIR / f"compliance_evidence_{run_id[:8]}.json"
    out_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "status": "success",
        "run_id": run_id,
        "evidence_path": str(out_path),
        "recommended_disclosures": disclosures,
    }
