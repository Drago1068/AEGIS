<#
.SYNOPSIS
  Verify a live AEGIS NAS deployment (Phase 7/9 + Phase 17 evidence gate). Distinct from package upload / deploy start.

.DESCRIPTION
  Checks /health, /ready, auth gates (including calibration-readiness), frontend reachability,
  optional authenticated research/readiness routes, and (when SSH is configured) Alembic current
  through migration 0008 / head. Use -DryRun to print the checklist without contacting the NAS
  (not acceptance evidence). See docs/architecture/decisions/0018-phase-17-nas-live-verification.md.

.EXAMPLE
  .\docker\nas\scripts\verify.ps1

.EXAMPLE
  .\docker\nas\scripts\verify.ps1 -DryRun
#>
param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "_common.ps1")

$RepoRoot = Get-RepoRoot -ScriptDir $ScriptDir
$EnvNas = Join-Path $RepoRoot ".env.nas"

$verifySymbol = "AAPL"
if (Test-Path -LiteralPath $EnvNas) {
    Import-DotEnvFile -Path $EnvNas
    if (-not [string]::IsNullOrWhiteSpace($env:AEGIS_NAS_VERIFY_SYMBOL)) {
        $verifySymbol = $env:AEGIS_NAS_VERIFY_SYMBOL.Trim().ToUpperInvariant()
    }
}

function Write-VerifyChecklist {
    param([string]$Symbol)
    Write-Host "Live verification checklist (ADR-0018):"
    Write-Host "  1. GET /health -> 200"
    Write-Host "  2. GET /ready -> 200"
    Write-Host "  3. Auth gate 401: watchlist, daily-bars, research latest, assessments list, calibration-readiness, evidence-summary, evidence-summary/export"
    Write-Host "  4. Frontend base URL -> 200|302|307|308"
    Write-Host "  5. POST /auth/login (operator credentials from .env.nas) -> 200 + cookie"
    Write-Host "  6. Authenticated GET /research/$Symbol/calibration-readiness -> 200"
    Write-Host "  7. Authenticated GET /research/$Symbol/assessments/latest -> 200|404"
    Write-Host "  8. Authenticated GET /research/$Symbol/assessments?limit= -> 200 (JSON array; [] OK)"
    Write-Host "  9. Authenticated GET .../assessments/{id}/calibrations and .../outcome-labels -> 200 (JSON array; [] OK)"
    Write-Host " 10. Authenticated GET /research/$Symbol/evidence-summary -> 200 (state=research_only; log present label + end-date keys when any)"
    Write-Host " 11. Authenticated GET /research/$Symbol/evidence-summary/export -> 200 (attachment, state=research_only)"
    Write-Host " 12. SSH alembic current includes 0008|head (when SSH configured)"
    Write-Host " 13. TLS profile: https:// URLs + Secure cookies when enabled"
}

if ($DryRun) {
    Write-Host "==> DRY RUN - checklist only; NOT live verification evidence"
    Write-VerifyChecklist -Symbol $verifySymbol
    Write-Host ""
    Write-Host "Dry-run complete. Run without -DryRun against a live NAS for acceptance evidence."
    exit 0
}

Require-EnvVars -Names @(
    "AEGIS_NAS_API_BASE_URL",
    "AEGIS_NAS_FRONTEND_BASE_URL",
    "AEGIS_OPERATOR_USERNAME",
    "AEGIS_OPERATOR_PASSWORD"
)

$api = $env:AEGIS_NAS_API_BASE_URL.TrimEnd("/")
$frontend = $env:AEGIS_NAS_FRONTEND_BASE_URL.TrimEnd("/")
$operatorUser = $env:AEGIS_OPERATOR_USERNAME
$operatorPassword = $env:AEGIS_OPERATOR_PASSWORD

if ($api -match "replace-with-" -or $frontend -match "replace-with-") {
    throw "AEGIS_NAS_API_BASE_URL / AEGIS_NAS_FRONTEND_BASE_URL still look like placeholders."
}
if ($operatorPassword -match "replace-with-|change-me-before-non-local-use") {
    throw "AEGIS_OPERATOR_PASSWORD still looks like a template placeholder."
}

if (Test-NasTlsEnabled) {
    if (-not $api.StartsWith("https://") -or -not $frontend.StartsWith("https://")) {
        throw ("TLS profile requires https:// verify URLs (API={0}; FRONTEND={1})." -f $api, $frontend)
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

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if ($null -eq $curl) {
    throw "curl.exe is required for verify.ps1 (OpenSSH/curl ships with modern Windows)."
}

function Get-HttpStatus {
    param(
        [string]$Url,
        [string]$CookieJar = ""
    )
    $curlArgs = @("-sS") + $curlInsecure + @("-o", "NUL", "-w", "%{http_code}", "--max-time", "30")
    if (-not [string]::IsNullOrWhiteSpace($CookieJar)) {
        $curlArgs += @("-b", $CookieJar)
    }
    $curlArgs += $Url
    $code = & curl.exe @curlArgs
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

Write-VerifyChecklist -Symbol $verifySymbol
Write-Host ""

Write-Host "==> Public health and readiness"
Assert-Status -Label "GET $api/health" -Actual (Get-HttpStatus "$api/health") -Expected @(200)
Assert-Status -Label "GET $api/ready" -Actual (Get-HttpStatus "$api/ready") -Expected @(200)

Write-Host "==> Auth gate (expect 401 without session)"
Assert-Status -Label "GET $api/watchlist" -Actual (Get-HttpStatus "$api/watchlist") -Expected @(401)
Assert-Status -Label "GET $api/market-data/$verifySymbol/daily-bars" -Actual (Get-HttpStatus "$api/market-data/$verifySymbol/daily-bars") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/assessments/latest" -Actual (Get-HttpStatus "$api/research/$verifySymbol/assessments/latest") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/assessments" -Actual (Get-HttpStatus "$api/research/$verifySymbol/assessments") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/calibration-readiness" -Actual (Get-HttpStatus "$api/research/$verifySymbol/calibration-readiness") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/evidence-summary" -Actual (Get-HttpStatus "$api/research/$verifySymbol/evidence-summary") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/evidence-summary/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/evidence-summary/export") -Expected @(401)

Write-Host "==> Frontend reachability"
$feStatus = Get-HttpStatus $frontend
Assert-Status -Label "GET $frontend" -Actual $feStatus -Expected @(200, 307, 308, 302)

Write-Host "==> Operator login + authenticated research diagnostics"
$cookieJar = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.cookies" -f [guid]::NewGuid().ToString("N"))
$loginFile = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.login.json" -f [guid]::NewGuid().ToString("N"))
try {
    # Write JSON to a file so PowerShell does not strip quotes when invoking curl.exe.
    $loginBody = (@{ username = $operatorUser; password = $operatorPassword } | ConvertTo-Json -Compress)
    [System.IO.File]::WriteAllText($loginFile, $loginBody, [System.Text.UTF8Encoding]::new($false))
    $loginCode = & curl.exe -sS @curlInsecure -o NUL -w "%{http_code}" --max-time 30 `
        -c $cookieJar -H "Content-Type: application/json" -H "Accept: application/json" `
        --data-binary "@$loginFile" "$api/auth/login"
    if ($LASTEXITCODE -ne 0) {
        throw "POST /auth/login request failed (curl exit $LASTEXITCODE)"
    }
    Assert-Status -Label "POST $api/auth/login" -Actual ([int]$loginCode) -Expected @(200)

    $readyCode = Get-HttpStatus "$api/research/$verifySymbol/calibration-readiness" -CookieJar $cookieJar
    Assert-Status -Label "GET $api/research/$verifySymbol/calibration-readiness (auth)" -Actual $readyCode -Expected @(200)

    $latestCode = Get-HttpStatus "$api/research/$verifySymbol/assessments/latest" -CookieJar $cookieJar
    Assert-Status -Label "GET $api/research/$verifySymbol/assessments/latest (auth)" -Actual $latestCode -Expected @(200, 404)

    # Phase 29: assessment history list (empty array is valid).
    $assessListUrl = "$api/research/$verifySymbol/assessments?limit=20"
    $assessListPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assessments.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $assessCode = & curl.exe -sS @curlInsecure -o $assessListPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $assessListUrl
        if ($LASTEXITCODE -ne 0) { throw "GET assessments list failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $assessListUrl (auth)" -Actual ([int]$assessCode) -Expected @(200)
        $assessBody = Get-Content -LiteralPath $assessListPath -Raw | ConvertFrom-Json
        if ($null -eq $assessBody) { throw "assessments list body was null" }
        Write-Host "OK  assessments list is JSON array (count=$(@($assessBody).Count))"
    } finally {
        if (Test-Path -LiteralPath $assessListPath) {
            Remove-Item -LiteralPath $assessListPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Phase 21: history list routes (empty array is valid). Prefer assessment id from latest when present.
    $historyAssessmentId = 1
    if ($latestCode -eq 200) {
        $latestBodyPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.latest.json" -f [guid]::NewGuid().ToString("N"))
        try {
            & curl.exe -sS @curlInsecure -o $latestBodyPath --max-time 30 -b $cookieJar `
                -H "Accept: application/json" "$api/research/$verifySymbol/assessments/latest" | Out-Null
            if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $latestBodyPath)) {
                $latestJson = Get-Content -LiteralPath $latestBodyPath -Raw | ConvertFrom-Json
                if ($null -ne $latestJson.id) {
                    $historyAssessmentId = [int]$latestJson.id
                }
            }
        } finally {
            if (Test-Path -LiteralPath $latestBodyPath) {
                Remove-Item -LiteralPath $latestBodyPath -Force -ErrorAction SilentlyContinue
            }
        }
    }

    $calibListUrl = "$api/research/$verifySymbol/assessments/$historyAssessmentId/calibrations"
    $labelListUrl = "$api/research/$verifySymbol/assessments/$historyAssessmentId/outcome-labels"
    $calibListPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.calibrations.json" -f [guid]::NewGuid().ToString("N"))
    $labelListPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.labels.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $calibCode = & curl.exe -sS @curlInsecure -o $calibListPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $calibListUrl
        if ($LASTEXITCODE -ne 0) { throw "GET calibrations list failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $calibListUrl (auth)" -Actual ([int]$calibCode) -Expected @(200)
        $calibBody = Get-Content -LiteralPath $calibListPath -Raw | ConvertFrom-Json
        if ($calibBody -isnot [System.Array] -and $null -ne $calibBody) {
            # ConvertFrom-Json may return a single object for one-element arrays; coerce via PowerShell.
            $calibBody = @($calibBody)
        }
        if ($null -eq $calibBody) { throw "calibrations list body was null" }
        Write-Host "OK  calibrations list is JSON array (count=$(@($calibBody).Count))"

        $labelCode = & curl.exe -sS @curlInsecure -o $labelListPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $labelListUrl
        if ($LASTEXITCODE -ne 0) { throw "GET outcome-labels list failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $labelListUrl (auth)" -Actual ([int]$labelCode) -Expected @(200)
        $labelBody = Get-Content -LiteralPath $labelListPath -Raw | ConvertFrom-Json
        if ($null -eq $labelBody) { throw "outcome-labels list body was null" }
        Write-Host "OK  outcome-labels list is JSON array (count=$(@($labelBody).Count))"
    } finally {
        foreach ($p in @($calibListPath, $labelListPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }

    # Phase 23: evidence summary aggregate (null/zero missing fields OK).
    $summaryUrl = "$api/research/$verifySymbol/evidence-summary"
    $summaryPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.summary.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $summaryCode = & curl.exe -sS @curlInsecure -o $summaryPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $summaryUrl
        if ($LASTEXITCODE -ne 0) { throw "GET evidence-summary failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $summaryUrl (auth)" -Actual ([int]$summaryCode) -Expected @(200)
        $summary = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
        if ($summary.state -ne "research_only") {
            throw "evidence-summary state expected research_only, got $($summary.state)"
        }
        if ($null -eq $summary.assessment_count -or [int]$summary.assessment_count -lt 0) {
            throw "evidence-summary assessment_count must be >= 0"
        }
        # Phase 27/31: log present label and end-date keys only (never invent).
        $labelKeys = @()
        $endDateKeys = @()
        if ($null -ne $summary.latest_outcome_label -and $null -ne $summary.latest_outcome_label.labels) {
            $labelKeys = @($summary.latest_outcome_label.labels.PSObject.Properties.Name)
        }
        if ($null -ne $summary.latest_outcome_label -and $null -ne $summary.latest_outcome_label.label_end_dates) {
            $endDateKeys = @($summary.latest_outcome_label.label_end_dates.PSObject.Properties.Name)
        }
        $labelPart = if ($labelKeys.Count -gt 0) { $labelKeys -join "," } else { "(none)" }
        $endPart = if ($endDateKeys.Count -gt 0) { $endDateKeys -join "," } else { "(none)" }
        Write-Host "OK  evidence-summary state=research_only assessments=$($summary.assessment_count) label_keys=$labelPart end_date_keys=$endPart"
    } finally {
        if (Test-Path -LiteralPath $summaryPath) {
            Remove-Item -LiteralPath $summaryPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Phase 25: evidence summary JSON export (attachment; same payload semantics).
    $exportUrl = "$api/research/$verifySymbol/evidence-summary/export"
    $exportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.export.json" -f [guid]::NewGuid().ToString("N"))
    $exportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.export.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $exportCode = & curl.exe -sS @curlInsecure -D $exportHeadersPath -o $exportPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $exportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET evidence-summary/export failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $exportUrl (auth)" -Actual ([int]$exportCode) -Expected @(200)
        $exportHeaders = Get-Content -LiteralPath $exportHeadersPath -Raw
        if ($exportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "evidence-summary/export missing Content-Disposition attachment"
        }
        $exportBody = Get-Content -LiteralPath $exportPath -Raw | ConvertFrom-Json
        if ($exportBody.state -ne "research_only") {
            throw "evidence-summary/export state expected research_only, got $($exportBody.state)"
        }
        if ($null -eq $exportBody.assessment_count -or [int]$exportBody.assessment_count -lt 0) {
            throw "evidence-summary/export assessment_count must be >= 0"
        }
        Write-Host "OK  evidence-summary/export attachment state=research_only assessments=$($exportBody.assessment_count)"
    } finally {
        foreach ($p in @($exportPath, $exportHeadersPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
finally {
    if (Test-Path -LiteralPath $cookieJar) {
        Remove-Item -LiteralPath $cookieJar -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $loginFile) {
        Remove-Item -LiteralPath $loginFile -Force -ErrorAction SilentlyContinue
    }
}

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
    $remote = ('{0}@{1}' -f $sshUser, $sshHost)
    $sshArgs = Get-SshArgs
    $dir = $remoteDir.TrimEnd("/")
    $cmd = @"
set -euo pipefail
cd '$dir'
out=`$(docker compose $composeFileArgs --env-file .env.nas --project-directory . exec -T backend alembic current)
echo "`$out"
echo "`$out" | grep -E '0008|head' >/dev/null
"@
    & ssh @sshArgs $remote $cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic current did not report migration 0008 / head. Apply alembic upgrade head on the NAS."
    }
    Write-Host "OK  alembic current includes 0008 / head"

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
    Write-Host "Expect revision 0008 (research_assessment_probability_calibrations) / head."
}

Write-Host ""
Write-Host "LIVE VERIFICATION PASSED for HTTP(S) checks against $api and $frontend (symbol=$verifySymbol)."
Write-Host "Upload/start alone is never sufficient; this verify step is the acceptance evidence."
Write-Host "Evidence: retain this stdout. Dry-run runs are not evidence."
