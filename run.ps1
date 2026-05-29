# RajISG Trust Agent (hackathon demo) — one-command launcher
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $Venv)) {
    $Venv = Join-Path $Root ".venv-agent"
}
$AgentDir = $PSScriptRoot
$EnvFile = Join-Path $AgentDir "rpca_compliance_agent\.env"
$ReqFile = Join-Path $AgentDir "requirements.txt"
if (-not (Test-Path $ReqFile)) {
    $ReqFile = Join-Path $Root "requirements-agent.txt"
}

function Import-DotEnv($Path) {
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        if ($line -match '^\s*([^=]+)\s*=\s*"?([^"]*)"?\s*$') {
            $name = $matches[1].Trim()
            $val = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $val
        }
    }
}

if (-not (Test-Path $Venv)) {
    Write-Host "Creating venv..."
    python -m venv $Venv
}

$Py = Join-Path $Venv "Scripts\python.exe"
$Pip = Join-Path $Venv "Scripts\pip.exe"
$Adk = Join-Path $Venv "Scripts\adk.exe"

& $Pip install -q -r $ReqFile

if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $AgentDir "rpca_compliance_agent\.env.example") $EnvFile
    Write-Host ""
    Write-Host "ACTION: Edit $EnvFile and set GOOGLE_API_KEY from https://aistudio.google.com/apikey"
    Write-Host ""
}

Import-DotEnv $EnvFile
# AI Studio key only — skip expired gcloud ADC for local demo
$env:GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
Remove-Item Env:GOOGLE_APPLICATION_CREDENTIALS -ErrorAction SilentlyContinue

if (-not $env:GOOGLE_API_KEY -or $env:GOOGLE_API_KEY -eq "YOUR_GEMINI_API_KEY") {
    Write-Host "ERROR: Set GOOGLE_API_KEY in $EnvFile"
    exit 1
}

Write-Host "Smoke test (validator only, no Gemini)..."
& $Py (Join-Path $AgentDir "smoke_test.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Port = if ($env:RPCA_ADK_PORT) { $env:RPCA_ADK_PORT } else { "8765" }

Write-Host ""
Write-Host "Auth: AI Studio API key (Vertex/gcloud disabled for this demo)"
Write-Host "Starting ADK web UI at http://localhost:$Port"
Write-Host "Select agent: rpca_compliance_agent"
Write-Host ""
Set-Location $AgentDir
& $Adk web --port $Port
