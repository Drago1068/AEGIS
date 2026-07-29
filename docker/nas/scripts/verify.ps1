<#
.SYNOPSIS
  Verify a live AEGIS NAS deployment (Phase 7 + optional Phase 9 TLS). Distinct from package upload / deploy start.

.DESCRIPTION
  Checks /health, /ready, auth gate (401 without session) on watchlist/daily-bars/research,
  frontend reachability, and (when SSH is configured) Alembic current + log guidance.
  When AEGIS_NAS_TLS_ENABLED=true, requires https:// verify URLs.

.EXAMPLE
  .\docker\nas\scripts\verify.ps1
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "_common.ps1")

$RepoRoot = Get-RepoRoot -ScriptDir $ScriptDir
$EnvNas = Join-Path $RepoRoot ".env.nas"
Import-DotEnvFile -Path $EnvNas
Require-EnvVars -Names @(
    "AEGIS_NAS_API_BASE_URL",
    "AEGIS_NAS_FRONTEND_BASE_URL"
)

$api = $env:AEGIS_NAS_API_BASE_URL.TrimEnd("/")
$frontend = $env:AEGIS_NAS_FRONTEND_BASE_URL.TrimEnd("/")

if ($api -match "replace-with-" -or $frontend -match "replace-with-") {
    throw "AEGIS_NAS_API_BASE_URL / AEGIS_NAS_FRONTEND_BASE_URL still look like placeholders."
}

if (Test-NasTlsEnabled) {
    # PEM presence already validated at package/deploy; verify focuses on HTTPS URLs.
    if (-not $api.StartsWith("https://") -or -not $frontend.StartsWith("https://")) {
        throw "TLS profile requires https:// verify URLs (API=$api, FRONTEND=$frontend)."
    }
    $secure = "$($env:AEGIS_SESSION_COOKIE_SECURE)".Trim().ToLowerInvariant()
    if ($secure -ne "true" -and $secure -ne "1") {
        throw "TLS profile requires AEGIS_SESSION_COOKIE_SECURE=true."
    }
    Write-Host "==> TLS profile enabled - verifying over HTTPS"
}

$curlInsecure = @()
$insecure = "$($env:AEGIS_NAS_VERIFY_CURL_INSECURE)".Trim().ToLowerInvariant()
if (@("true", "1", "yes") -contains $insecure) {
    Write-Host "NOTE: AEGIS_NAS_VERIFY_CURL_INSECURE set - curl will skip TLS certificate verification (lab only)."
    $curlInsecure = @("-k")
}

function Get-HttpStatus {
    param([string]$Url)
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($null -eq $curl) {
        throw "curl.exe is required for verify.ps1 (OpenSSH/curl ships with modern Windows)."
    }
    $code = & curl.exe -sS @curlInsecure -o NUL -w "%{http_code}" --max-time 30 $Url
    if ($LASTEXITCODE -ne 0) {
        throw "HTTP request failed for $Url (curl exit $LASTEXITCODE)"
    }
    return [int]$code
}

function Assert-Status {
    param([string]$Label, [int]$Actual, [int[]]$Expected)
    if ($Expected -notcontains $Actual) {
        throw "$Label : expected HTTP $($Expected -join '|'), got $Actual"
    }
    Write-Host "OK  $Label -> $Actual"
}

Write-Host "==> Public health and readiness"
Assert-Status -Label "GET $api/health" -Actual (Get-HttpStatus "$api/health") -Expected @(200)
Assert-Status -Label "GET $api/ready" -Actual (Get-HttpStatus "$api/ready") -Expected @(200)

Write-Host "==> Auth gate (expect 401 without session)"
Assert-Status -Label "GET $api/watchlist" -Actual (Get-HttpStatus "$api/watchlist") -Expected @(401)
Assert-Status -Label "GET $api/market-data/AAPL/daily-bars" -Actual (Get-HttpStatus "$api/market-data/AAPL/daily-bars") -Expected @(401)
Assert-Status -Label "GET $api/research/AAPL/assessments/latest" -Actual (Get-HttpStatus "$api/research/AAPL/assessments/latest") -Expected @(401)

Write-Host "==> Frontend reachability"
$feStatus = Get-HttpStatus $frontend
Assert-Status -Label "GET $frontend" -Actual $feStatus -Expected @(200, 307, 308, 302)

$composeFileFlags = Get-ComposeNasRemoteFileFlags
$composeFileArgs = ($composeFileFlags -join " ")

$sshHost = $env:AEGIS_NAS_SSH_HOST
$sshUser = $env:AEGIS_NAS_SSH_USER
$remoteDir = $env:AEGIS_NAS_REMOTE_DIR
if (
    -not [string]::IsNullOrWhiteSpace($sshHost) -and
    -not ($sshHost -match "^(replace-with-|your-)") -and
    -not [string]::IsNullOrWhiteSpace($sshUser) -and
    -not [string]::IsNullOrWhiteSpace($remoteDir)
) {
    Write-Host "==> Alembic current (via SSH)"
    $remote = "{0}@{1}" -f $sshUser, $sshHost
    $sshArgs = Get-SshArgs
    $dir = $remoteDir.TrimEnd("/")
    $cmd = @"
set -euo pipefail
cd '$dir'
out=`$(docker compose $composeFileArgs --env-file .env.nas --project-directory . exec -T backend alembic current)
echo "`$out"
echo "`$out" | grep -E '0005|head' >/dev/null
"@
    & ssh @sshArgs $remote $cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic current did not report migration 0005 / head. Apply alembic upgrade head on the NAS."
    }
    Write-Host "OK  alembic current includes 0005 / head"

    Write-Host ""
    Write-Host "Log inspection guidance (run on NAS or via SSH):"
    Write-Host "  docker compose $composeFileArgs --env-file .env.nas logs --tail=200 backend"
    Write-Host "  docker compose $composeFileArgs --env-file .env.nas logs --tail=200 frontend"
    if (Test-NasTlsEnabled) {
        Write-Host "  docker compose $composeFileArgs --env-file .env.nas logs --tail=200 caddy"
    }
    Write-Host "  docker compose $composeFileArgs --env-file .env.nas ps"
} else {
    Write-Host ""
    Write-Host "NOTE: SSH vars not fully set; skipped remote Alembic check."
    Write-Host "On the NAS, confirm: docker compose ... exec -T backend alembic current"
    Write-Host "Expect revision 0005 (research_assessment_snapshots) / head."
}

Write-Host ""
Write-Host "Verification passed for HTTP(S) checks against $api and $frontend."
Write-Host "Upload/start alone is never sufficient; this verify step is the acceptance evidence."
