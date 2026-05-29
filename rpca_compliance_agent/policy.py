"""Policy control snippets for agent grounding (not legal advice)."""

from __future__ import annotations

from typing import Any, Dict, List

EU_ART50_CONTROLS: List[Dict[str, str]] = [
    {
        "id": "eu50-ai-interaction",
        "title": "AI interaction transparency",
        "control": "Disclose when users interact with an AI system (not a human).",
    },
    {
        "id": "eu50-synthetic-marking",
        "title": "Synthetic content marking",
        "control": "Mark AI-generated or AI-manipulated content in machine-readable form where required.",
    },
    {
        "id": "eu50-deepfake-public-interest",
        "title": "Deepfake / public-interest labeling",
        "control": "Label deepfakes and manipulated content in public-interest contexts.",
    },
    {
        "id": "eu50-provenance-evidence",
        "title": "Inspectable provenance",
        "control": "Retain validation outcomes and manifest exports for audit (C2PA-aligned).",
    },
]

INDIA_IT_RULES_CONTROLS: List[Dict[str, str]] = [
    {
        "id": "in-synthetic-warning",
        "title": "Synthetic media warnings",
        "control": "Surface user-visible warnings for synthetic or manipulated media at publish/reshare.",
    },
    {
        "id": "in-diligence-metadata",
        "title": "Platform diligence",
        "control": "Support inspectable provenance signals for due-diligence workflows.",
    },
    {
        "id": "in-reshare-behaviour",
        "title": "Resharing behaviour",
        "control": "Preserve or re-surface disclosure when content is reshared downstream.",
    },
    {
        "id": "in-evidence-export",
        "title": "Evidence for institutions",
        "control": "Export validation JSON + human summary for legal / compliance review.",
    },
]

JURISDICTION_MAP = {
    "eu": EU_ART50_CONTROLS,
    "india": INDIA_IT_RULES_CONTROLS,
    "both": EU_ART50_CONTROLS + INDIA_IT_RULES_CONTROLS,
    "global": EU_ART50_CONTROLS + INDIA_IT_RULES_CONTROLS,
}


def get_controls(jurisdiction: str) -> Dict[str, Any]:
    key = (jurisdiction or "both").strip().lower()
    controls = JURISDICTION_MAP.get(key, JURISDICTION_MAP["both"])
    return {
        "jurisdiction": key,
        "disclaimer": (
            "Policy mapping supports operational controls only — not legal advice. "
            "Customer counsel owns final obligations."
        ),
        "controls": controls,
    }


def recommend_disclosures(
    *,
    validation_status_public: str,
    jurisdiction: str = "both",
) -> List[str]:
    """Deterministic disclosure hints from verdict (agent may elaborate in prose)."""
    status = (validation_status_public or "").strip().lower()
    recs: List[str] = []
    if status in ("trusted", "valid"):
        recs.append("Content credentials verified — retain verify link and manifest export for audit.")
    elif status == "unrecognized":
        recs.append("Signer not on C2PA trust list — disclose limited assurance; do not claim 'trusted' globally.")
    elif status in ("invalid", "incomplete", "no credentials"):
        recs.append("No reliable provenance — apply synthetic-media warning if AI-generated or manipulated.")
    else:
        recs.append("Review validation outcome before publication; default to conservative disclosure.")

    if jurisdiction in ("eu", "both", "global"):
        recs.append("EU Art. 50: ensure AI/synthetic marking matches deployer role and user-facing surfaces.")
    if jurisdiction in ("india", "both", "global"):
        recs.append("India IT Rules alignment: user warning + diligence-friendly evidence export.")
    return recs
