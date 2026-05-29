# RajISG Trust Agent

**Google for Startups AI Agents Challenge** — Build (Net-New Agents)

Autonomous agent: **cryptographic C2PA validation first**, then **EU Art. 50 / India IT Rules** control mapping, then **audit evidence export**.

Built on live [RajISG Provenance & Content Authenticity (RPCA)](https://contentauthenticity.rajisg.com/validate) — not a mock.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy rpca_compliance_agent\.env.example rpca_compliance_agent\.env
# Set GOOGLE_API_KEY in .env — https://aistudio.google.com/apikey
powershell -ExecutionPolicy Bypass -File run.ps1
```

Open http://localhost:8765 → select **rpca_compliance_agent**.

## Demo prompt

```
Validate for EU and India and export evidence:
C:\path\to\your\image.jpg
```

## Architecture

```
User → ADK Agent (Gemini) → tools:
  validate_content_credentials → contentauthenticity.rajisg.com (live RPCA API)
  get_policy_controls          → EU / India control library
  export_compliance_evidence   → output/*.json
```

## Stack

Google ADK · Gemini · Python · RPCA validator API (Cloud Run)

**Note:** Operational compliance mapping only — not legal advice. Signing is a separate RajISG pilot; this demo covers verify + evidence.
