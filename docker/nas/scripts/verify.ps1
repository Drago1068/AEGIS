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
    Write-Host "  3. Auth gate 401: watchlist, daily-bars, research latest, assessments list(+export), calibration-readiness(+export), outcome-labels/export, calibrations/export, evidence-summary(+export), outcome-labels/backfill POST, assessments/backfill POST"
    Write-Host "  4. Frontend base URL -> 200|302|307|308"
    Write-Host "  5. POST /auth/login (operator credentials from .env.nas) -> 200 + cookie"
    Write-Host "  6. Authenticated GET /research/$Symbol/calibration-readiness -> 200 (by_horizon includes fwd5+fwd20)"
    Write-Host "  7. Authenticated GET /research/$Symbol/calibration-readiness/export -> 200 (attachment; by_horizon present)"
    Write-Host "  8. Authenticated GET /research/$Symbol/assessments/latest -> 200|404"
    Write-Host "  9. Authenticated GET /research/$Symbol/assessments?limit= -> 200 (JSON array; [] OK)"
    Write-Host " 10. Authenticated GET /research/$Symbol/assessments/export -> 200 (attachment, JSON array; [] OK)"
    Write-Host " 11. Authenticated POST /research/$Symbol/assessments/backfill -> 200 (summary counts; zeros OK)"
    Write-Host " 12. Authenticated POST /research/$Symbol/outcome-labels/backfill -> 200 (summary counts; if assessments persisted>0 then labels persisted>=1)"
    Write-Host " 13. Authenticated POST .../assessments/{id}/calibrations?horizon=forward_return_5 -> 200|422"
    Write-Host " 14. Authenticated GET .../assessments/{id}/calibrations and .../outcome-labels -> 200 (JSON array; [] OK)"
    Write-Host " 15. Authenticated GET .../assessments/{id}/outcome-labels/export -> 200 (attachment, JSON array; [] OK)"
    Write-Host " 16. Authenticated GET .../assessments/{id}/calibrations/export -> 200 (attachment, JSON array; [] OK)"
    Write-Host " 17. Authenticated GET /research/$Symbol/evidence-summary -> 200 (state=research_only; log present label + end-date keys when any)"
    Write-Host " 18. Authenticated GET /research/$Symbol/evidence-summary/export -> 200 (attachment, state=research_only)"
    Write-Host " 19. SSH alembic current includes 0009|head (when SSH configured)"
    Write-Host " 20. SSH .env.nas includes AEGIS_RESEARCH_BAR_LOAD_LIMIT in bounds (Phase 52)"
    Write-Host " 21. SSH .env.nas includes AEGIS_DAILY_BAR_OUTPUT_SIZE=full (Phase 54)"
    Write-Host " 22. SSH .env.nas includes AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true (Phase 56)"
    Write-Host " 23. Authenticated POST outcome-labels/backfill?limit=100 (Phase 58 source-aware throughput)"
    Write-Host " 24. Authenticated evidence-summary includes Phase 59 provenance fields"
    Write-Host " 25. Authenticated assessments list+export with component_source=mixed (Phase 62)"
    Write-Host " 26. Phase 64: frontend redeploy includes Phase 63 one-click mixed filter (unit-tested; API via item 25)"
    Write-Host " 27. Phase 66: backend redeploy includes Phase 65 prefer-mixed label backfill (limit=100 path)"
    Write-Host " 28. Authenticated evidence-summary includes Phase 67 mixed label coverage fields"
    Write-Host " 29. Authenticated evidence-summary includes Phase 69 mixed_labeled_assessment_count (Phase 70)"
    Write-Host " 30. Phase 72: frontend redeploy includes Phase 71 corpus callout (unit-tested; readiness nested fields)"
    Write-Host " 31. Phase 74: frontend redeploy includes Phase 73 by_horizon mini-rows (unit-tested; nested readiness)"
    Write-Host " 32. Authenticated evidence-summary nested calibration_readiness.by_horizon includes fwd5+fwd20 (Phase 75)"
    Write-Host " 33. Authenticated evidence-summary nested corpus/bucket readiness fields (Phase 76)"
    Write-Host " 34. Phase 78: frontend redeploy includes Phase 77 horizon detail expand (unit-tested)"
    Write-Host " 35. Authenticated evidence-summary most_recent_labeled_* fields (Phase 80)"
    Write-Host " 36. Phase 82: frontend redeploy includes Phase 81 load-scan-labeled control (unit-tested)"
    Write-Host " 37. Phase 84: frontend redeploy includes Phase 83 assessment-id caption (unit-tested)"
    Write-Host " 38. Phase 86: frontend redeploy includes Phase 85 load-kind caption (unit-tested)"
    Write-Host " 39. Phase 88: frontend redeploy includes Phase 87 download-loaded-assessment (unit-tested)"
    Write-Host " 40. Phase 90: frontend redeploy includes Phase 89 download-names-assessment (unit-tested)"
    Write-Host " 41. Phase 92: frontend redeploy includes Phase 91 empty-state-loaded-assessment (unit-tested)"
    Write-Host " 42. Phase 94: frontend redeploy includes Phase 93 compute-loaded-assessment (unit-tested)"
    Write-Host " 43. Phase 96: frontend redeploy includes Phase 95 backfill-refresh-loaded-assessment (unit-tested)"
    Write-Host " 44. Phase 98: frontend redeploy includes Phase 97 assessment-backfill-preserves-labels (unit-tested)"
    Write-Host " 45. Phase 100: frontend redeploy includes Phase 99 calibrations-download-names-latest (unit-tested)"
    Write-Host " 46. Phase 102: frontend redeploy includes Phase 101 compute-calibration-names-latest (unit-tested)"
    Write-Host " 47. Phase 104: frontend redeploy includes Phase 103 calibration-note-scan-labeled (unit-tested)"
    Write-Host " 48. Phase 106: frontend redeploy includes Phase 105 load-labels-for-latest (unit-tested)"
    Write-Host " 49. Phase 108: frontend redeploy includes Phase 107 active-assessment-id-rename (unit-tested)"
    Write-Host " 50. Phase 110: frontend redeploy includes Phase 109 handlers-use-active-assessment-id (unit-tested)"
    Write-Host " 51. Phase 112: frontend redeploy includes Phase 111 resolve-outcome-label-load-kind (unit-tested)"
    Write-Host " 52. Phase 114: frontend redeploy includes Phase 113 outcome-label-aria-load-kind (unit-tested)"
    Write-Host " 53. Phase 116: frontend redeploy includes Phase 115 extract-outcome-label-helpers (unit-tested)"
    Write-Host " 54. Phase 118: frontend redeploy includes Phase 117 outcome-label-id-chip-load-kind (unit-tested)"
    Write-Host " 55. Phase 120: frontend redeploy includes Phase 119 calibration-chips-name-latest (unit-tested)"
    Write-Host " 56. Phase 122: frontend redeploy includes Phase 121 backfill-names-refresh-target (unit-tested)"
    Write-Host " 57. Phase 124: frontend redeploy includes Phase 123 extract-action-toolbar (unit-tested)"
    Write-Host " 58. Phase 126: frontend redeploy includes Phase 125 group-action-toolbar (unit-tested)"
    Write-Host " 59. Phase 128: frontend redeploy includes Phase 127 extract-outcome-label-history-section (unit-tested)"
    Write-Host " 60. Phase 130: frontend redeploy includes Phase 129 extract-assessment-history-section (unit-tested)"
    Write-Host " 61. Phase 132: frontend redeploy includes Phase 131 extract-calibration-readiness-section (unit-tested)"
    Write-Host " 62. Phase 134: frontend redeploy includes Phase 133 extract-probability-calibration-section (unit-tested)"
    Write-Host " 63. Phase 136: frontend redeploy includes Phase 135 extract-evidence-summary-section (unit-tested)"
    Write-Host " 64. Phase 138: frontend redeploy includes Phase 137 extract-latest-assessment-section (unit-tested)"
    Write-Host " 65. Phase 140: frontend redeploy includes Phase 139 extract-backfill-status-section (unit-tested)"
    Write-Host " 66. Phase 142: frontend redeploy includes Phase 141 extract-panel-header (unit-tested)"
    Write-Host " 67. Phase 144: frontend redeploy includes Phase 143 extract-error-alert (unit-tested)"
    Write-Host " 68. Authenticated evidence-summary includes Phase 145 labeled/unlabeled scan counts (Phase 146)"
    Write-Host " 69. Authenticated evidence-summary includes Phase 147 latest_coverage_confidence (Phase 148)"
    Write-Host " 70. Authenticated evidence-summary includes Phase 149 latest_research_index (Phase 150)"
    Write-Host " 71. Authenticated evidence-summary includes Phase 151 latest_as_of_trading_date (Phase 152)"
    Write-Host " 72. Authenticated evidence-summary includes Phase 153 latest_bar_count (Phase 154)"
    Write-Host " 73. Authenticated evidence-summary includes Phase 155 latest_input_source (Phase 156)"
    Write-Host " 74. Authenticated evidence-summary includes Phase 157 latest_method_id (Phase 158)"
    Write-Host " 75. Authenticated evidence-summary includes Phase 159 latest_method_version (Phase 160)"
    Write-Host " 76. Authenticated evidence-summary includes Phase 161 latest_lookback_end_date (Phase 162)"
    Write-Host " 77. Authenticated evidence-summary includes Phase 163 latest_lookback_start_date (Phase 164)"
    Write-Host " 78. Authenticated evidence-summary includes Phase 165 latest_schema_version (Phase 166)"
    Write-Host " 79. Authenticated evidence-summary includes Phase 167 latest_computed_at (Phase 168)"
    Write-Host " 80. Authenticated evidence-summary includes Phase 169 latest_event_time (Phase 170)"
    Write-Host " 81. Authenticated evidence-summary includes Phase 171 latest_probability_confidence (Phase 172)"
    Write-Host " 82. Authenticated evidence-summary includes Phase 173 latest_assessment_id (Phase 174)"
    Write-Host " 83. Authenticated evidence-summary includes Phase 175 latest_outcome_label_id (Phase 176)"
    Write-Host " 84. Authenticated evidence-summary includes Phase 177 latest_calibration_id (Phase 178)"
    Write-Host " 85. Authenticated evidence-summary includes Phase 179 latest_calibration_horizon_key (Phase 180)"
    Write-Host " 86. Authenticated evidence-summary includes Phase 181 latest_calibration_computed_at (Phase 182)"
    Write-Host " 87. Authenticated evidence-summary includes Phase 183 latest_calibration_corpus_count (Phase 184)"
    Write-Host " 88. Authenticated evidence-summary includes Phase 185 latest_calibration_bucket_count (Phase 186)"
    Write-Host " 89. Authenticated evidence-summary includes Phase 187 latest_calibration_method_id (Phase 188)"
    Write-Host " 90. Authenticated evidence-summary includes Phase 189 latest_calibration_method_version (Phase 190)"
    Write-Host " 91. Authenticated evidence-summary includes Phase 191 latest_calibration_schema_version (Phase 192)"
    Write-Host " 92. Authenticated evidence-summary includes Phase 193 latest_calibration_state (Phase 194)"
    Write-Host " 93. Authenticated evidence-summary includes Phase 195 latest_calibration_probability_confidence (Phase 196)"
    Write-Host " 94. Authenticated evidence-summary includes Phase 197 latest_calibration_assessment_snapshot_id (Phase 198)"
    Write-Host " 95. Authenticated evidence-summary includes Phase 199 latest_outcome_label_computed_at (Phase 200)"
    Write-Host " 96. Authenticated evidence-summary includes Phase 201 latest_outcome_label_method_id (Phase 202)"
    Write-Host " 97. Authenticated evidence-summary includes Phase 203 latest_outcome_label_method_version (Phase 204)"
    Write-Host " 98. Authenticated evidence-summary includes Phase 205 latest_outcome_label_schema_version (Phase 206)"
    Write-Host " 99. Authenticated evidence-summary includes Phase 207 latest_outcome_label_state (Phase 208)"
    Write-Host "100. Authenticated evidence-summary includes Phase 209 latest_outcome_label_bar_source (Phase 210)"
    Write-Host "101. Authenticated evidence-summary includes Phase 211 latest_outcome_label_as_of_trading_date (Phase 212)"
    Write-Host "102. Authenticated evidence-summary includes Phase 213 most_recent_labeled_outcome_label_id (Phase 214)"
    Write-Host "103. Authenticated evidence-summary includes Phase 215 most_recent_labeled_outcome_label_method_id (Phase 216)"
    Write-Host "104. Authenticated evidence-summary includes Phase 217 most_recent_labeled_outcome_label_method_version (Phase 218)"
    Write-Host "105. Authenticated evidence-summary includes Phase 219 most_recent_labeled_outcome_label_schema_version (Phase 220)"
    Write-Host "106. Authenticated evidence-summary includes Phase 221 most_recent_labeled_outcome_label_state (Phase 222)"
    Write-Host "107. Authenticated evidence-summary includes Phase 223 most_recent_labeled_outcome_label_bar_source (Phase 224)"
    Write-Host "108. Authenticated evidence-summary includes Phase 225 most_recent_labeled_outcome_label_computed_at (Phase 226)"
    Write-Host "109. Authenticated evidence-summary includes Phase 227 most_recent_labeled_outcome_label_as_of_trading_date (Phase 228)"
    Write-Host "110. Authenticated evidence-summary includes Phase 229 scan_labeled_freshness_lag_trading_days (Phase 230)"
    Write-Host "111. Authenticated evidence-summary includes Phase 231 latest_assessment_is_label_ready (Phase 232)"
    Write-Host "112. Authenticated evidence-summary includes Phase 233 latest_assessment_label_block_reason (Phase 234)"
    Write-Host "113. Authenticated evidence-summary includes Phase 235 most_recent_labelable_as_of_trading_date (Phase 236)"
    Write-Host "114. Authenticated evidence-summary includes Phase 237 most_recent_unlabeled_labelable_as_of_trading_date (Phase 238)"
    Write-Host "115. Authenticated evidence-summary includes Phase 239 scan_unlabeled_label_ready_count (Phase 240)"
    Write-Host "116. TLS profile: https:// URLs + Secure cookies when enabled"
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
$resolveRaw = "$($env:AEGIS_NAS_VERIFY_CURL_RESOLVE)".Trim()
if (-not [string]::IsNullOrWhiteSpace($resolveRaw)) {
    foreach ($entry in ($resolveRaw -split ',')) {
        $trimmed = $entry.Trim()
        if (-not [string]::IsNullOrWhiteSpace($trimmed)) {
            $curlInsecure += @("--resolve", $trimmed)
        }
    }
    Write-Host "NOTE: AEGIS_NAS_VERIFY_CURL_RESOLVE set - curl --resolve overrides for lab DNS."
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
Assert-Status -Label "GET $api/research/$verifySymbol/assessments/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/assessments/export") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/calibration-readiness" -Actual (Get-HttpStatus "$api/research/$verifySymbol/calibration-readiness") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/calibration-readiness/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/calibration-readiness/export") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/assessments/1/outcome-labels/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/assessments/1/outcome-labels/export") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/assessments/1/calibrations/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/assessments/1/calibrations/export") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/evidence-summary" -Actual (Get-HttpStatus "$api/research/$verifySymbol/evidence-summary") -Expected @(401)
Assert-Status -Label "GET $api/research/$verifySymbol/evidence-summary/export" -Actual (Get-HttpStatus "$api/research/$verifySymbol/evidence-summary/export") -Expected @(401)
$backfillUnauthUrl = "$api/research/$verifySymbol/outcome-labels/backfill?limit=20"
$backfillUnauthCode = & curl.exe -sS @curlInsecure -o NUL -w "%{http_code}" --max-time 30 `
    -H "Accept: application/json" -X POST $backfillUnauthUrl
if ($LASTEXITCODE -ne 0) { throw "POST outcome-labels/backfill (unauth) failed (curl exit $LASTEXITCODE)" }
Assert-Status -Label "POST $backfillUnauthUrl (unauth)" -Actual ([int]$backfillUnauthCode) -Expected @(401)
$assessBackfillUnauthUrl = "$api/research/$verifySymbol/assessments/backfill?limit=20"
$assessBackfillUnauthCode = & curl.exe -sS @curlInsecure -o NUL -w "%{http_code}" --max-time 30 `
    -H "Accept: application/json" -X POST $assessBackfillUnauthUrl
if ($LASTEXITCODE -ne 0) { throw "POST assessments/backfill (unauth) failed (curl exit $LASTEXITCODE)" }
Assert-Status -Label "POST $assessBackfillUnauthUrl (unauth)" -Actual ([int]$assessBackfillUnauthCode) -Expected @(401)

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

    # Phase 42: multi-horizon readiness diagnostics (by_horizon).
    $readyBodyPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.readiness-body.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $readyFetchCode = & curl.exe -sS @curlInsecure -o $readyBodyPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" "$api/research/$verifySymbol/calibration-readiness"
        if ($LASTEXITCODE -ne 0) { throw "GET calibration-readiness body failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET calibration-readiness body (auth)" -Actual ([int]$readyFetchCode) -Expected @(200)
        $readyBody = Get-Content -LiteralPath $readyBodyPath -Raw | ConvertFrom-Json
        if ($null -eq $readyBody.by_horizon) { throw "calibration-readiness missing by_horizon" }
        $horizonKeys = @($readyBody.by_horizon | ForEach-Object { [string]$_.outcome_horizon_key })
        foreach ($required in @("forward_return_5", "forward_return_20")) {
            if ($horizonKeys -notcontains $required) {
                throw "calibration-readiness by_horizon missing $required (got: $($horizonKeys -join ','))"
            }
        }
        Write-Host "OK  calibration-readiness by_horizon keys=$($horizonKeys -join ',')"
    } finally {
        if (Test-Path -LiteralPath $readyBodyPath) {
            Remove-Item -LiteralPath $readyBodyPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Phase 33: calibration readiness JSON export (attachment).
    $readyExportUrl = "$api/research/$verifySymbol/calibration-readiness/export"
    $readyExportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.readiness.json" -f [guid]::NewGuid().ToString("N"))
    $readyExportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.readiness.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $readyExportCode = & curl.exe -sS @curlInsecure -D $readyExportHeadersPath -o $readyExportPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $readyExportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET calibration-readiness/export failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $readyExportUrl (auth)" -Actual ([int]$readyExportCode) -Expected @(200)
        $readyExportHeaders = Get-Content -LiteralPath $readyExportHeadersPath -Raw
        if ($readyExportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "calibration-readiness/export missing Content-Disposition attachment"
        }
        $readyExportBody = Get-Content -LiteralPath $readyExportPath -Raw | ConvertFrom-Json
        if ([string]::IsNullOrWhiteSpace([string]$readyExportBody.status)) {
            throw "calibration-readiness/export missing status"
        }
        if ($null -eq $readyExportBody.by_horizon) {
            throw "calibration-readiness/export missing by_horizon"
        }
        Write-Host "OK  calibration-readiness/export attachment status=$($readyExportBody.status) by_horizon_count=$(@($readyExportBody.by_horizon).Count)"
    } finally {
        foreach ($p in @($readyExportPath, $readyExportHeadersPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }

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

    # Phase 39: assessment history JSON export (attachment; [] OK).
    $assessExportUrl = "$api/research/$verifySymbol/assessments/export?limit=20"
    $assessExportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assess-export.json" -f [guid]::NewGuid().ToString("N"))
    $assessExportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assess-export.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $assessExportCode = & curl.exe -sS @curlInsecure -D $assessExportHeadersPath -o $assessExportPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $assessExportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET assessments/export failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $assessExportUrl (auth)" -Actual ([int]$assessExportCode) -Expected @(200)
        $assessExportHeaders = Get-Content -LiteralPath $assessExportHeadersPath -Raw
        if ($assessExportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "assessments/export missing Content-Disposition attachment"
        }
        $assessExportBody = Get-Content -LiteralPath $assessExportPath -Raw | ConvertFrom-Json
        if ($null -eq $assessExportBody) { throw "assessments/export body was null" }
        Write-Host "OK  assessments/export attachment JSON array (count=$(@($assessExportBody).Count))"
    } finally {
        foreach ($p in @($assessExportPath, $assessExportHeadersPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }

    # Phase 62: assessment history filtered by component_source=mixed (Phase 61).
    $mixedListUrl = "$api/research/$verifySymbol/assessments?limit=20&component_source=mixed"
    $mixedListPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assessments-mixed.json" -f [guid]::NewGuid().ToString("N"))
    $mixedListCount = 0
    try {
        $mixedListCode = & curl.exe -sS @curlInsecure -o $mixedListPath -w "%{http_code}" --max-time 60 `
            -b $cookieJar -H "Accept: application/json" $mixedListUrl
        if ($LASTEXITCODE -ne 0) { throw "GET assessments?component_source=mixed failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $mixedListUrl (auth)" -Actual ([int]$mixedListCode) -Expected @(200)
        $mixedListBody = Get-Content -LiteralPath $mixedListPath -Raw | ConvertFrom-Json
        if ($null -eq $mixedListBody) { throw "assessments?component_source=mixed body was null" }
        $mixedListCount = @($mixedListBody).Count
        foreach ($row in @($mixedListBody)) {
            $src = $null
            if ($null -ne $row.components -and $null -ne $row.components.component_source) {
                $src = [string]$row.components.component_source
            }
            if ([string]::IsNullOrWhiteSpace($src)) {
                $src = [string]$row.input_source
            }
            if ($src -ne "mixed") {
                throw "assessments?component_source=mixed returned non-mixed row id=$($row.id) src=$src"
            }
        }
        Write-Host "OK  assessments?component_source=mixed JSON array (count=$mixedListCount)"
    } finally {
        if (Test-Path -LiteralPath $mixedListPath) {
            Remove-Item -LiteralPath $mixedListPath -Force -ErrorAction SilentlyContinue
        }
    }

    $mixedExportUrl = "$api/research/$verifySymbol/assessments/export?limit=20&component_source=mixed"
    $mixedExportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assess-export-mixed.json" -f [guid]::NewGuid().ToString("N"))
    $mixedExportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assess-export-mixed.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $mixedExportCode = & curl.exe -sS @curlInsecure -D $mixedExportHeadersPath -o $mixedExportPath -w "%{http_code}" --max-time 60 `
            -b $cookieJar -H "Accept: application/json" $mixedExportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET assessments/export?component_source=mixed failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $mixedExportUrl (auth)" -Actual ([int]$mixedExportCode) -Expected @(200)
        $mixedExportHeaders = Get-Content -LiteralPath $mixedExportHeadersPath -Raw
        if ($mixedExportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "assessments/export?component_source=mixed missing Content-Disposition attachment"
        }
        $mixedExportBody = Get-Content -LiteralPath $mixedExportPath -Raw | ConvertFrom-Json
        if ($null -eq $mixedExportBody) { throw "assessments/export?component_source=mixed body was null" }
        Write-Host "OK  assessments/export?component_source=mixed attachment JSON array (count=$(@($mixedExportBody).Count))"
        Write-Host "OK  Phase 62 assessments component_source=mixed list+export"
    } finally {
        foreach ($p in @($mixedExportPath, $mixedExportHeadersPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }

    # Phase 46/48: assessment backfill then outcome-label backfill.
    # Phase 48: if assessments persisted>0, labels must persist >=1 (label-ready candidates).
    $assessBackfillUrl = "$api/research/$verifySymbol/assessments/backfill?limit=20"
    $assessBackfillPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.assess-backfill.json" -f [guid]::NewGuid().ToString("N"))
    $assessPersisted = 0
    try {
        $assessBackfillCode = & curl.exe -sS @curlInsecure -o $assessBackfillPath -w "%{http_code}" --max-time 120 `
            -b $cookieJar -H "Accept: application/json" -X POST $assessBackfillUrl
        if ($LASTEXITCODE -ne 0) { throw "POST assessments/backfill failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "POST $assessBackfillUrl (auth)" -Actual ([int]$assessBackfillCode) -Expected @(200)
        $assessBackfillBody = Get-Content -LiteralPath $assessBackfillPath -Raw | ConvertFrom-Json
        if ($null -eq $assessBackfillBody.candidate_count) { throw "assessments/backfill missing candidate_count" }
        if ($null -eq $assessBackfillBody.persisted_count) { throw "assessments/backfill missing persisted_count" }
        if ($null -eq $assessBackfillBody.skipped_count) { throw "assessments/backfill missing skipped_count" }
        $assessPersisted = [int]$assessBackfillBody.persisted_count
        Write-Host "OK  assessments/backfill candidate_count=$($assessBackfillBody.candidate_count) persisted=$assessPersisted skipped=$($assessBackfillBody.skipped_count)"
    } finally {
        if (Test-Path -LiteralPath $assessBackfillPath) {
            Remove-Item -LiteralPath $assessBackfillPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Phase 44/48: outcome-label backfill (always 200 summary; Phase 48 coupling when assessments persisted).
    $backfillUrl = "$api/research/$verifySymbol/outcome-labels/backfill?limit=20"
    $backfillPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.backfill.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $backfillCode = & curl.exe -sS @curlInsecure -o $backfillPath -w "%{http_code}" --max-time 60 `
            -b $cookieJar -H "Accept: application/json" -X POST $backfillUrl
        if ($LASTEXITCODE -ne 0) { throw "POST outcome-labels/backfill failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "POST $backfillUrl (auth)" -Actual ([int]$backfillCode) -Expected @(200)
        $backfillBody = Get-Content -LiteralPath $backfillPath -Raw | ConvertFrom-Json
        if ($null -eq $backfillBody.assessment_count) { throw "backfill missing assessment_count" }
        if ($null -eq $backfillBody.persisted_count) { throw "backfill missing persisted_count" }
        if ($null -eq $backfillBody.skipped_count) { throw "backfill missing skipped_count" }
        $labelPersisted = [int]$backfillBody.persisted_count
        Write-Host "OK  outcome-labels/backfill assessment_count=$($backfillBody.assessment_count) persisted=$labelPersisted skipped=$($backfillBody.skipped_count)"
        if ($assessPersisted -gt 0 -and $labelPersisted -lt 1) {
            throw "Phase 48: assessments/backfill persisted=$assessPersisted but outcome-labels/backfill persisted=$labelPersisted (expected >=1 for label-ready candidates)"
        }
        if ($assessPersisted -gt 0) {
            Write-Host "OK  Phase 48/50 label-ready coupling at limit=20 (assessments persisted=$assessPersisted -> labels persisted=$labelPersisted)"
        } else {
            Write-Host "OK  Phase 48/50 label-ready coupling skipped (assessments persisted=0; label zeros OK)"
        }
    } finally {
        if (Test-Path -LiteralPath $backfillPath) {
            Remove-Item -LiteralPath $backfillPath -Force -ErrorAction SilentlyContinue
        }
    }

    # Phase 58: source-aware throughput path (ADR-0059).
    $backfill100Url = "$api/research/$verifySymbol/outcome-labels/backfill?limit=100"
    $backfill100Path = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.backfill100.json" -f [guid]::NewGuid().ToString("N"))
    try {
        $backfill100Code = & curl.exe -sS @curlInsecure -o $backfill100Path -w "%{http_code}" --max-time 120 `
            -b $cookieJar -H "Accept: application/json" -X POST $backfill100Url
        if ($LASTEXITCODE -ne 0) { throw "POST outcome-labels/backfill?limit=100 failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "POST $backfill100Url (auth)" -Actual ([int]$backfill100Code) -Expected @(200)
        $backfill100Body = Get-Content -LiteralPath $backfill100Path -Raw | ConvertFrom-Json
        if ($null -eq $backfill100Body.assessment_count) { throw "backfill100 missing assessment_count" }
        if ($null -eq $backfill100Body.persisted_count) { throw "backfill100 missing persisted_count" }
        if ($null -eq $backfill100Body.skipped_count) { throw "backfill100 missing skipped_count" }
        $label100Assess = [int]$backfill100Body.assessment_count
        $label100Persisted = [int]$backfill100Body.persisted_count
        $label100Skipped = [int]$backfill100Body.skipped_count
        Write-Host "OK  outcome-labels/backfill?limit=100 assessment_count=$label100Assess persisted=$label100Persisted skipped=$label100Skipped"
        if ($label100Assess -gt 0 -and $label100Persisted -lt 1) {
            throw "Phase 58: limit=100 selected $label100Assess candidates but persisted=$label100Persisted (expected >=1 when source-ready candidates exist)"
        }
        if ($label100Assess -gt 0 -and $label100Skipped -gt $label100Persisted) {
            Write-Host "WARN Phase 58: skipped ($label100Skipped) exceeded persisted ($label100Persisted); source-aware selection should usually keep skips low"
        }
        Write-Host "OK  Phase 58 source-aware label backfill throughput check"
        Write-Host "OK  Phase 66 prefer-mixed label backfill path exercised (limit=100)"
    } finally {
        if (Test-Path -LiteralPath $backfill100Path) {
            Remove-Item -LiteralPath $backfill100Path -Force -ErrorAction SilentlyContinue
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

    # Phase 42: POST calibrations?horizon= (200 or fail-closed 422 OK; uses latest id when present).
    $calibPostUrl = "$api/research/$verifySymbol/assessments/$historyAssessmentId/calibrations?horizon=forward_return_5"
    $calibPostCode = & curl.exe -sS @curlInsecure -o NUL -w "%{http_code}" --max-time 30 `
        -b $cookieJar -H "Accept: application/json" -X POST $calibPostUrl
    if ($LASTEXITCODE -ne 0) { throw "POST calibrations?horizon= failed (curl exit $LASTEXITCODE)" }
    Assert-Status -Label "POST $calibPostUrl (auth)" -Actual ([int]$calibPostCode) -Expected @(200, 422)
    Write-Host "OK  POST calibrations?horizon=forward_return_5 -> $calibPostCode (200 or fail-closed 422)"

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

    # Phase 35: outcome-labels history JSON export (attachment; [] OK).
    $labelExportUrl = "$api/research/$verifySymbol/assessments/$historyAssessmentId/outcome-labels/export?limit=20"
    $labelExportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.labels-export.json" -f [guid]::NewGuid().ToString("N"))
    $labelExportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.labels-export.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $labelExportCode = & curl.exe -sS @curlInsecure -D $labelExportHeadersPath -o $labelExportPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $labelExportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET outcome-labels/export failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $labelExportUrl (auth)" -Actual ([int]$labelExportCode) -Expected @(200)
        $labelExportHeaders = Get-Content -LiteralPath $labelExportHeadersPath -Raw
        if ($labelExportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "outcome-labels/export missing Content-Disposition attachment"
        }
        $labelExportBody = Get-Content -LiteralPath $labelExportPath -Raw | ConvertFrom-Json
        if ($null -eq $labelExportBody) { throw "outcome-labels/export body was null" }
        Write-Host "OK  outcome-labels/export attachment JSON array (count=$(@($labelExportBody).Count))"
    } finally {
        foreach ($p in @($labelExportPath, $labelExportHeadersPath)) {
            if (Test-Path -LiteralPath $p) {
                Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            }
        }
    }

    # Phase 37: calibrations history JSON export (attachment; [] OK).
    $calibExportUrl = "$api/research/$verifySymbol/assessments/$historyAssessmentId/calibrations/export?limit=20"
    $calibExportPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.calib-export.json" -f [guid]::NewGuid().ToString("N"))
    $calibExportHeadersPath = Join-Path ([System.IO.Path]::GetTempPath()) ("aegis-nas-verify-{0}.calib-export.hdr" -f [guid]::NewGuid().ToString("N"))
    try {
        $calibExportCode = & curl.exe -sS @curlInsecure -D $calibExportHeadersPath -o $calibExportPath -w "%{http_code}" --max-time 30 `
            -b $cookieJar -H "Accept: application/json" $calibExportUrl
        if ($LASTEXITCODE -ne 0) { throw "GET calibrations/export failed (curl exit $LASTEXITCODE)" }
        Assert-Status -Label "GET $calibExportUrl (auth)" -Actual ([int]$calibExportCode) -Expected @(200)
        $calibExportHeaders = Get-Content -LiteralPath $calibExportHeadersPath -Raw
        if ($calibExportHeaders -notmatch '(?i)content-disposition:.*attachment') {
            throw "calibrations/export missing Content-Disposition attachment"
        }
        $calibExportBody = Get-Content -LiteralPath $calibExportPath -Raw | ConvertFrom-Json
        if ($null -eq $calibExportBody) { throw "calibrations/export body was null" }
        Write-Host "OK  calibrations/export attachment JSON array (count=$(@($calibExportBody).Count))"
    } finally {
        foreach ($p in @($calibExportPath, $calibExportHeadersPath)) {
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
        # Phase 60: provenance fields from Phase 59 (null/zero OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_component_source")) {
            throw "evidence-summary missing latest_component_source (Phase 59/60)"
        }
        if (-not ($summary.PSObject.Properties.Name -contains "latest_resolved_label_bar_source")) {
            throw "evidence-summary missing latest_resolved_label_bar_source (Phase 59/60)"
        }
        if ($null -eq $summary.mixed_component_source_assessment_count -or [int]$summary.mixed_component_source_assessment_count -lt 0) {
            throw "evidence-summary mixed_component_source_assessment_count must be >= 0"
        }
        $compSrc = if ($null -eq $summary.latest_component_source) { "null" } else { $summary.latest_component_source }
        $labelSrc = if ($null -eq $summary.latest_resolved_label_bar_source) { "null" } else { $summary.latest_resolved_label_bar_source }
        Write-Host "OK  evidence-summary state=research_only assessments=$($summary.assessment_count) label_keys=$labelPart end_date_keys=$endPart component_source=$compSrc label_bar_source=$labelSrc mixed_count=$($summary.mixed_component_source_assessment_count)"
        Write-Host "OK  Phase 60 evidence-summary provenance fields present"
        if ([int]$summary.mixed_component_source_assessment_count -gt 0 -and $mixedListCount -lt 1) {
            throw "Phase 62: mixed_component_source_assessment_count=$($summary.mixed_component_source_assessment_count) but assessments?component_source=mixed returned 0"
        }
        if ([int]$summary.mixed_component_source_assessment_count -gt 0) {
            Write-Host "OK  Phase 62 mixed filter non-empty when mixed_count=$($summary.mixed_component_source_assessment_count) (filtered=$mixedListCount)"
        }
        # Phase 68: mixed label coverage fields from Phase 67.
        if (-not ($summary.PSObject.Properties.Name -contains "mixed_unlabeled_assessment_count")) {
            throw "evidence-summary missing mixed_unlabeled_assessment_count (Phase 67/68)"
        }
        if ($null -eq $summary.mixed_unlabeled_assessment_count -or [int]$summary.mixed_unlabeled_assessment_count -lt 0) {
            throw "evidence-summary mixed_unlabeled_assessment_count must be >= 0"
        }
        if (-not ($summary.PSObject.Properties.Name -contains "latest_mixed_label_bar_source")) {
            throw "evidence-summary missing latest_mixed_label_bar_source (Phase 67/68)"
        }
        if ([int]$summary.mixed_unlabeled_assessment_count -gt [int]$summary.mixed_component_source_assessment_count) {
            throw "evidence-summary mixed_unlabeled_assessment_count exceeds mixed_component_source_assessment_count"
        }
        $mixedUnlabeled = [int]$summary.mixed_unlabeled_assessment_count
        $mixedTotal = [int]$summary.mixed_component_source_assessment_count
        $mixedLabelSrc = if ($null -eq $summary.latest_mixed_label_bar_source) { "null" } else { $summary.latest_mixed_label_bar_source }
        if ($mixedTotal -gt 0 -and $mixedUnlabeled -lt $mixedTotal -and $null -eq $summary.latest_mixed_label_bar_source) {
            throw "Phase 68: mixed labeled rows exist but latest_mixed_label_bar_source is null"
        }
        Write-Host "OK  Phase 68 mixed label coverage mixed_unlabeled=$mixedUnlabeled latest_mixed_label_bar_source=$mixedLabelSrc"
        # Phase 70: explicit mixed labeled count from Phase 69.
        if (-not ($summary.PSObject.Properties.Name -contains "mixed_labeled_assessment_count")) {
            throw "evidence-summary missing mixed_labeled_assessment_count (Phase 69/70)"
        }
        if ($null -eq $summary.mixed_labeled_assessment_count -or [int]$summary.mixed_labeled_assessment_count -lt 0) {
            throw "evidence-summary mixed_labeled_assessment_count must be >= 0"
        }
        $mixedLabeled = [int]$summary.mixed_labeled_assessment_count
        if (($mixedLabeled + $mixedUnlabeled) -ne $mixedTotal) {
            throw "Phase 70: mixed_labeled($mixedLabeled)+mixed_unlabeled($mixedUnlabeled) != mixed_count($mixedTotal)"
        }
        Write-Host "OK  Phase 70 mixed labeled coverage mixed_labeled=$mixedLabeled mixed_unlabeled=$mixedUnlabeled mixed_count=$mixedTotal"
        # Phase 75: nested readiness by_horizon on evidence-summary (Phase 73 UI contract).
        if ($null -eq $summary.calibration_readiness) {
            throw "evidence-summary missing calibration_readiness (Phase 75)"
        }
        if ($null -eq $summary.calibration_readiness.by_horizon) {
            throw "evidence-summary.calibration_readiness missing by_horizon (Phase 75)"
        }
        $summaryHorizonKeys = @(
            $summary.calibration_readiness.by_horizon | ForEach-Object { [string]$_.outcome_horizon_key }
        )
        foreach ($required in @("forward_return_5", "forward_return_20")) {
            if ($summaryHorizonKeys -notcontains $required) {
                throw ("evidence-summary.calibration_readiness.by_horizon missing {0} (got: {1})" -f `
                    $required, ($summaryHorizonKeys -join ","))
            }
        }
        Write-Host ("OK  Phase 75 evidence-summary by_horizon keys={0}" -f ($summaryHorizonKeys -join ","))
        # Phase 76: nested corpus/bucket fields for Phase 71 callout contract.
        foreach ($field in @("corpus_count", "bucket_count")) {
            if (-not ($summary.calibration_readiness.PSObject.Properties.Name -contains $field)) {
                throw "evidence-summary.calibration_readiness missing $field (Phase 76)"
            }
            if ($null -eq $summary.calibration_readiness.$field -or [int]$summary.calibration_readiness.$field -lt 0) {
                throw "evidence-summary.calibration_readiness.$field must be >= 0 (Phase 76)"
            }
        }
        foreach ($field in @("min_corpus", "min_bucket")) {
            if (-not ($summary.calibration_readiness.PSObject.Properties.Name -contains $field)) {
                throw "evidence-summary.calibration_readiness missing $field (Phase 76)"
            }
            if ($null -eq $summary.calibration_readiness.$field -or [int]$summary.calibration_readiness.$field -lt 1) {
                throw "evidence-summary.calibration_readiness.$field must be >= 1 (Phase 76)"
            }
        }
        Write-Host ("OK  Phase 76 evidence-summary corpus={0}/min {1} bucket={2}/min {3}" -f `
            $summary.calibration_readiness.corpus_count,
            $summary.calibration_readiness.min_corpus,
            $summary.calibration_readiness.bucket_count,
            $summary.calibration_readiness.min_bucket)
        # Phase 80: most-recent labeled fields from Phase 79 (null OK when none labeled).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_assessment_id")) {
            throw "evidence-summary missing most_recent_labeled_assessment_id (Phase 79/80)"
        }
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label (Phase 79/80)"
        }
        $mrlId = $summary.most_recent_labeled_assessment_id
        $mrlLabel = $summary.most_recent_labeled_outcome_label
        if ($null -eq $mrlId -and $null -ne $mrlLabel) {
            throw "Phase 80: most_recent_labeled_outcome_label set but assessment_id is null"
        }
        if ($null -ne $mrlId -and $null -eq $mrlLabel) {
            throw "Phase 80: most_recent_labeled_assessment_id set but outcome_label is null"
        }
        if ($null -ne $mrlId -and [int]$mrlId -lt 1) {
            throw "Phase 80: most_recent_labeled_assessment_id must be >= 1 when set"
        }
        $mrlPart = if ($null -eq $mrlId) { "null" } else { [string]$mrlId }
        Write-Host "OK  Phase 80 most_recent_labeled_assessment_id=$mrlPart"
        # Phase 146: scan-wide labeled/unlabeled counts from Phase 145.
        if (-not ($summary.PSObject.Properties.Name -contains "labeled_assessment_count")) {
            throw "evidence-summary missing labeled_assessment_count (Phase 145/146)"
        }
        if (-not ($summary.PSObject.Properties.Name -contains "unlabeled_assessment_count")) {
            throw "evidence-summary missing unlabeled_assessment_count (Phase 145/146)"
        }
        $labeledScan = [int]$summary.labeled_assessment_count
        $unlabeledScan = [int]$summary.unlabeled_assessment_count
        $assessScan = [int]$summary.assessment_count
        if ($labeledScan -lt 0 -or $unlabeledScan -lt 0) {
            throw "Phase 146: labeled/unlabeled scan counts must be >= 0"
        }
        if (($labeledScan + $unlabeledScan) -ne $assessScan) {
            throw "Phase 146: labeled($labeledScan)+unlabeled($unlabeledScan) != assessment_count($assessScan)"
        }
        Write-Host "OK  Phase 146 scan label coverage labeled=$labeledScan unlabeled=$unlabeledScan assessments=$assessScan"
        # Phase 148: latest_coverage_confidence from Phase 147 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_coverage_confidence")) {
            throw "evidence-summary missing latest_coverage_confidence (Phase 147/148)"
        }
        $cov = $summary.latest_coverage_confidence
        if ($null -ne $cov) {
            $covNum = [double]$cov
            if ($covNum -lt 0.0 -or $covNum -gt 1.0) {
                throw "Phase 148: latest_coverage_confidence must be in [0,1] when set"
            }
        }
        $covPart = if ($null -eq $cov) { "null" } else { [string]$cov }
        Write-Host "OK  Phase 148 latest_coverage_confidence=$covPart"
        # Phase 150: latest_research_index from Phase 149 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_research_index")) {
            throw "evidence-summary missing latest_research_index (Phase 149/150)"
        }
        $idx = $summary.latest_research_index
        if ($null -ne $idx -and ($idx -isnot [ValueType])) {
            throw "Phase 150: latest_research_index must be numeric or null"
        }
        $idxPart = if ($null -eq $idx) { "null" } else { [string]$idx }
        Write-Host "OK  Phase 150 latest_research_index=$idxPart"
        # Phase 152: latest_as_of_trading_date from Phase 151 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_as_of_trading_date")) {
            throw "evidence-summary missing latest_as_of_trading_date (Phase 151/152)"
        }
        $asOf = $summary.latest_as_of_trading_date
        $asOfPart = if ($null -eq $asOf) { "null" } else { [string]$asOf }
        Write-Host "OK  Phase 152 latest_as_of_trading_date=$asOfPart"
        # Phase 154: latest_bar_count from Phase 153 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_bar_count")) {
            throw "evidence-summary missing latest_bar_count (Phase 153/154)"
        }
        $bars = $summary.latest_bar_count
        if ($null -ne $bars -and [int]$bars -lt 0) {
            throw "Phase 154: latest_bar_count must be >= 0 when set"
        }
        $barsPart = if ($null -eq $bars) { "null" } else { [string]$bars }
        Write-Host "OK  Phase 154 latest_bar_count=$barsPart"
        # Phase 156: latest_input_source from Phase 155 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_input_source")) {
            throw "evidence-summary missing latest_input_source (Phase 155/156)"
        }
        $inSrc = $summary.latest_input_source
        $inSrcPart = if ($null -eq $inSrc) { "null" } else { [string]$inSrc }
        Write-Host "OK  Phase 156 latest_input_source=$inSrcPart"
        # Phase 158: latest_method_id from Phase 157 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_method_id")) {
            throw "evidence-summary missing latest_method_id (Phase 157/158)"
        }
        $methodId = $summary.latest_method_id
        $methodPart = if ($null -eq $methodId) { "null" } else { [string]$methodId }
        Write-Host "OK  Phase 158 latest_method_id=$methodPart"
        # Phase 160: latest_method_version from Phase 159 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_method_version")) {
            throw "evidence-summary missing latest_method_version (Phase 159/160)"
        }
        $methodVer = $summary.latest_method_version
        if ($null -ne $methodVer -and [int]$methodVer -lt 1) {
            throw "Phase 160: latest_method_version must be >= 1 when set"
        }
        $methodVerPart = if ($null -eq $methodVer) { "null" } else { [string]$methodVer }
        Write-Host "OK  Phase 160 latest_method_version=$methodVerPart"
        # Phase 162: latest_lookback_end_date from Phase 161 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_lookback_end_date")) {
            throw "evidence-summary missing latest_lookback_end_date (Phase 161/162)"
        }
        $lookbackEnd = $summary.latest_lookback_end_date
        $lookbackPart = if ($null -eq $lookbackEnd) { "null" } else { [string]$lookbackEnd }
        Write-Host "OK  Phase 162 latest_lookback_end_date=$lookbackPart"
        # Phase 164: latest_lookback_start_date from Phase 163 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_lookback_start_date")) {
            throw "evidence-summary missing latest_lookback_start_date (Phase 163/164)"
        }
        $lookbackStart = $summary.latest_lookback_start_date
        $lookbackStartPart = if ($null -eq $lookbackStart) { "null" } else { [string]$lookbackStart }
        Write-Host "OK  Phase 164 latest_lookback_start_date=$lookbackStartPart"
        # Phase 166: latest_schema_version from Phase 165 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_schema_version")) {
            throw "evidence-summary missing latest_schema_version (Phase 165/166)"
        }
        $schemaVer = $summary.latest_schema_version
        if ($null -ne $schemaVer -and [int]$schemaVer -lt 1) {
            throw "Phase 166: latest_schema_version must be >= 1 when set"
        }
        $schemaPart = if ($null -eq $schemaVer) { "null" } else { [string]$schemaVer }
        Write-Host "OK  Phase 166 latest_schema_version=$schemaPart"
        # Phase 168: latest_computed_at from Phase 167 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_computed_at")) {
            throw "evidence-summary missing latest_computed_at (Phase 167/168)"
        }
        $computedAt = $summary.latest_computed_at
        $computedPart = if ($null -eq $computedAt -or $computedAt -eq "") { "null" } else { [string]$computedAt }
        Write-Host "OK  Phase 168 latest_computed_at=$computedPart"
        # Phase 170: latest_event_time from Phase 169 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_event_time")) {
            throw "evidence-summary missing latest_event_time (Phase 169/170)"
        }
        $eventTime = $summary.latest_event_time
        $eventPart = if ($null -eq $eventTime -or $eventTime -eq "") { "null" } else { [string]$eventTime }
        Write-Host "OK  Phase 170 latest_event_time=$eventPart"
        # Phase 172: latest_probability_confidence from Phase 171 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_probability_confidence")) {
            throw "evidence-summary missing latest_probability_confidence (Phase 171/172)"
        }
        $probConf = $summary.latest_probability_confidence
        if ($null -ne $probConf) {
            $pc = [double]$probConf
            if ($pc -lt 0.0 -or $pc -gt 1.0) {
                throw "Phase 172: latest_probability_confidence must be in [0,1] when set"
            }
        }
        $probPart = if ($null -eq $probConf) { "null" } else { [string]$probConf }
        Write-Host "OK  Phase 172 latest_probability_confidence=$probPart"
        # Phase 174: latest_assessment_id from Phase 173 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_assessment_id")) {
            throw "evidence-summary missing latest_assessment_id (Phase 173/174)"
        }
        $assessId = $summary.latest_assessment_id
        if ($null -ne $assessId -and [int]$assessId -lt 1) {
            throw "Phase 174: latest_assessment_id must be >= 1 when set"
        }
        $assessIdPart = if ($null -eq $assessId) { "null" } else { [string]$assessId }
        Write-Host "OK  Phase 174 latest_assessment_id=$assessIdPart"
        # Phase 176: latest_outcome_label_id from Phase 175 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_id")) {
            throw "evidence-summary missing latest_outcome_label_id (Phase 175/176)"
        }
        $labelId = $summary.latest_outcome_label_id
        if ($null -ne $labelId -and [int]$labelId -lt 1) {
            throw "Phase 176: latest_outcome_label_id must be >= 1 when set"
        }
        $labelIdPart = if ($null -eq $labelId) { "null" } else { [string]$labelId }
        Write-Host "OK  Phase 176 latest_outcome_label_id=$labelIdPart"
        # Phase 178: latest_calibration_id from Phase 177 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_id")) {
            throw "evidence-summary missing latest_calibration_id (Phase 177/178)"
        }
        $calId = $summary.latest_calibration_id
        if ($null -ne $calId -and [int]$calId -lt 1) {
            throw "Phase 178: latest_calibration_id must be >= 1 when set"
        }
        $calIdPart = if ($null -eq $calId) { "null" } else { [string]$calId }
        Write-Host "OK  Phase 178 latest_calibration_id=$calIdPart"
        # Phase 180: latest_calibration_horizon_key from Phase 179 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_horizon_key")) {
            throw "evidence-summary missing latest_calibration_horizon_key (Phase 179/180)"
        }
        $horizonKey = $summary.latest_calibration_horizon_key
        $horizonPart = if ($null -eq $horizonKey -or $horizonKey -eq "") { "null" } else { [string]$horizonKey }
        Write-Host "OK  Phase 180 latest_calibration_horizon_key=$horizonPart"
        # Phase 182: latest_calibration_computed_at from Phase 181 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_computed_at")) {
            throw "evidence-summary missing latest_calibration_computed_at (Phase 181/182)"
        }
        $calComputedAt = $summary.latest_calibration_computed_at
        $calComputedPart = if ($null -eq $calComputedAt -or $calComputedAt -eq "") { "null" } else { [string]$calComputedAt }
        Write-Host "OK  Phase 182 latest_calibration_computed_at=$calComputedPart"
        # Phase 184: latest_calibration_corpus_count from Phase 183 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_corpus_count")) {
            throw "evidence-summary missing latest_calibration_corpus_count (Phase 183/184)"
        }
        $corpusCount = $summary.latest_calibration_corpus_count
        if ($null -ne $corpusCount -and [int]$corpusCount -lt 0) {
            throw "Phase 184: latest_calibration_corpus_count must be >= 0 when set"
        }
        $corpusPart = if ($null -eq $corpusCount) { "null" } else { [string]$corpusCount }
        Write-Host "OK  Phase 184 latest_calibration_corpus_count=$corpusPart"
        # Phase 186: latest_calibration_bucket_count from Phase 185 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_bucket_count")) {
            throw "evidence-summary missing latest_calibration_bucket_count (Phase 185/186)"
        }
        $bucketCount = $summary.latest_calibration_bucket_count
        if ($null -ne $bucketCount -and [int]$bucketCount -lt 0) {
            throw "Phase 186: latest_calibration_bucket_count must be >= 0 when set"
        }
        $bucketPart = if ($null -eq $bucketCount) { "null" } else { [string]$bucketCount }
        Write-Host "OK  Phase 186 latest_calibration_bucket_count=$bucketPart"
        # Phase 188: latest_calibration_method_id from Phase 187 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_method_id")) {
            throw "evidence-summary missing latest_calibration_method_id (Phase 187/188)"
        }
        $calMethodId = $summary.latest_calibration_method_id
        $calMethodPart = if ($null -eq $calMethodId -or $calMethodId -eq "") { "null" } else { [string]$calMethodId }
        Write-Host "OK  Phase 188 latest_calibration_method_id=$calMethodPart"
        # Phase 190: latest_calibration_method_version from Phase 189 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_method_version")) {
            throw "evidence-summary missing latest_calibration_method_version (Phase 189/190)"
        }
        $calMethodVer = $summary.latest_calibration_method_version
        if ($null -ne $calMethodVer -and [int]$calMethodVer -lt 1) {
            throw "Phase 190: latest_calibration_method_version must be >= 1 when set"
        }
        $calMethodVerPart = if ($null -eq $calMethodVer) { "null" } else { [string]$calMethodVer }
        Write-Host "OK  Phase 190 latest_calibration_method_version=$calMethodVerPart"
        # Phase 192: latest_calibration_schema_version from Phase 191 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_schema_version")) {
            throw "evidence-summary missing latest_calibration_schema_version (Phase 191/192)"
        }
        $calSchemaVer = $summary.latest_calibration_schema_version
        if ($null -ne $calSchemaVer -and [int]$calSchemaVer -lt 1) {
            throw "Phase 192: latest_calibration_schema_version must be >= 1 when set"
        }
        $calSchemaVerPart = if ($null -eq $calSchemaVer) { "null" } else { [string]$calSchemaVer }
        Write-Host "OK  Phase 192 latest_calibration_schema_version=$calSchemaVerPart"
        # Phase 194: latest_calibration_state from Phase 193 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_state")) {
            throw "evidence-summary missing latest_calibration_state (Phase 193/194)"
        }
        $calState = $summary.latest_calibration_state
        $calStatePart = if ($null -eq $calState -or $calState -eq "") { "null" } else { [string]$calState }
        Write-Host "OK  Phase 194 latest_calibration_state=$calStatePart"
        # Phase 196: latest_calibration_probability_confidence from Phase 195 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_probability_confidence")) {
            throw "evidence-summary missing latest_calibration_probability_confidence (Phase 195/196)"
        }
        $calProbConf = $summary.latest_calibration_probability_confidence
        if ($null -ne $calProbConf) {
            $cpf = [double]$calProbConf
            if ($cpf -lt 0 -or $cpf -gt 1) {
                throw "Phase 196: latest_calibration_probability_confidence must be in [0,1] when set"
            }
        }
        $calProbPart = if ($null -eq $calProbConf) { "null" } else { [string]$calProbConf }
        Write-Host "OK  Phase 196 latest_calibration_probability_confidence=$calProbPart"
        # Phase 198: latest_calibration_assessment_snapshot_id from Phase 197 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_calibration_assessment_snapshot_id")) {
            throw "evidence-summary missing latest_calibration_assessment_snapshot_id (Phase 197/198)"
        }
        $calSnapId = $summary.latest_calibration_assessment_snapshot_id
        if ($null -ne $calSnapId -and [int]$calSnapId -lt 1) {
            throw "Phase 198: latest_calibration_assessment_snapshot_id must be >= 1 when set"
        }
        $calSnapPart = if ($null -eq $calSnapId) { "null" } else { [string]$calSnapId }
        Write-Host "OK  Phase 198 latest_calibration_assessment_snapshot_id=$calSnapPart"
        # Phase 200: latest_outcome_label_computed_at from Phase 199 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_computed_at")) {
            throw "evidence-summary missing latest_outcome_label_computed_at (Phase 199/200)"
        }
        $labelComputedAt = $summary.latest_outcome_label_computed_at
        $labelComputedPart = if ($null -eq $labelComputedAt -or $labelComputedAt -eq "") { "null" } else { [string]$labelComputedAt }
        Write-Host "OK  Phase 200 latest_outcome_label_computed_at=$labelComputedPart"
        # Phase 202: latest_outcome_label_method_id from Phase 201 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_method_id")) {
            throw "evidence-summary missing latest_outcome_label_method_id (Phase 201/202)"
        }
        $labelMethodId = $summary.latest_outcome_label_method_id
        $labelMethodPart = if ($null -eq $labelMethodId -or $labelMethodId -eq "") { "null" } else { [string]$labelMethodId }
        Write-Host "OK  Phase 202 latest_outcome_label_method_id=$labelMethodPart"
        # Phase 204: latest_outcome_label_method_version from Phase 203 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_method_version")) {
            throw "evidence-summary missing latest_outcome_label_method_version (Phase 203/204)"
        }
        $labelMethodVersion = $summary.latest_outcome_label_method_version
        $labelVersionPart = if ($null -eq $labelMethodVersion -or $labelMethodVersion -eq "") { "null" } else { [string]$labelMethodVersion }
        Write-Host "OK  Phase 204 latest_outcome_label_method_version=$labelVersionPart"
        # Phase 206: latest_outcome_label_schema_version from Phase 205 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_schema_version")) {
            throw "evidence-summary missing latest_outcome_label_schema_version (Phase 205/206)"
        }
        $labelSchemaVersion = $summary.latest_outcome_label_schema_version
        $labelSchemaPart = if ($null -eq $labelSchemaVersion -or $labelSchemaVersion -eq "") { "null" } else { [string]$labelSchemaVersion }
        Write-Host "OK  Phase 206 latest_outcome_label_schema_version=$labelSchemaPart"
        # Phase 208: latest_outcome_label_state from Phase 207 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_state")) {
            throw "evidence-summary missing latest_outcome_label_state (Phase 207/208)"
        }
        $labelState = $summary.latest_outcome_label_state
        $labelStatePart = if ($null -eq $labelState -or $labelState -eq "") { "null" } else { [string]$labelState }
        Write-Host "OK  Phase 208 latest_outcome_label_state=$labelStatePart"
        # Phase 210: latest_outcome_label_bar_source from Phase 209 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_bar_source")) {
            throw "evidence-summary missing latest_outcome_label_bar_source (Phase 209/210)"
        }
        $labelBarSource = $summary.latest_outcome_label_bar_source
        $labelBarPart = if ($null -eq $labelBarSource -or $labelBarSource -eq "") { "null" } else { [string]$labelBarSource }
        Write-Host "OK  Phase 210 latest_outcome_label_bar_source=$labelBarPart"
        # Phase 212: latest_outcome_label_as_of_trading_date from Phase 211 (null OK).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_outcome_label_as_of_trading_date")) {
            throw "evidence-summary missing latest_outcome_label_as_of_trading_date (Phase 211/212)"
        }
        $labelAsOf = $summary.latest_outcome_label_as_of_trading_date
        $labelAsOfPart = if ($null -eq $labelAsOf -or $labelAsOf -eq "") { "null" } else { [string]$labelAsOf }
        Write-Host "OK  Phase 212 latest_outcome_label_as_of_trading_date=$labelAsOfPart"
        # Phase 214: most_recent_labeled_outcome_label_id from Phase 213 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_id")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_id (Phase 213/214)"
        }
        $scanLabelId = $summary.most_recent_labeled_outcome_label_id
        $scanLabelPart = if ($null -eq $scanLabelId -or $scanLabelId -eq "") { "null" } else { [string]$scanLabelId }
        Write-Host "OK  Phase 214 most_recent_labeled_outcome_label_id=$scanLabelPart"
        # Phase 216: most_recent_labeled_outcome_label_method_id from Phase 215 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_method_id")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_method_id (Phase 215/216)"
        }
        $scanLabelMethodId = $summary.most_recent_labeled_outcome_label_method_id
        $scanLabelMethodPart = if ($null -eq $scanLabelMethodId -or $scanLabelMethodId -eq "") { "null" } else { [string]$scanLabelMethodId }
        Write-Host "OK  Phase 216 most_recent_labeled_outcome_label_method_id=$scanLabelMethodPart"
        # Phase 218: most_recent_labeled_outcome_label_method_version from Phase 217 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_method_version")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_method_version (Phase 217/218)"
        }
        $scanLabelMethodVersion = $summary.most_recent_labeled_outcome_label_method_version
        $scanLabelMethodVersionPart = if ($null -eq $scanLabelMethodVersion -or $scanLabelMethodVersion -eq "") { "null" } else { [string]$scanLabelMethodVersion }
        Write-Host "OK  Phase 218 most_recent_labeled_outcome_label_method_version=$scanLabelMethodVersionPart"
        # Phase 220: most_recent_labeled_outcome_label_schema_version from Phase 219 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_schema_version")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_schema_version (Phase 219/220)"
        }
        $scanLabelSchemaVersion = $summary.most_recent_labeled_outcome_label_schema_version
        $scanLabelSchemaVersionPart = if ($null -eq $scanLabelSchemaVersion -or $scanLabelSchemaVersion -eq "") { "null" } else { [string]$scanLabelSchemaVersion }
        Write-Host "OK  Phase 220 most_recent_labeled_outcome_label_schema_version=$scanLabelSchemaVersionPart"
        # Phase 222: most_recent_labeled_outcome_label_state from Phase 221 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_state")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_state (Phase 221/222)"
        }
        $scanLabelState = $summary.most_recent_labeled_outcome_label_state
        $scanLabelStatePart = if ($null -eq $scanLabelState -or $scanLabelState -eq "") { "null" } else { [string]$scanLabelState }
        Write-Host "OK  Phase 222 most_recent_labeled_outcome_label_state=$scanLabelStatePart"
        # Phase 224: most_recent_labeled_outcome_label_bar_source from Phase 223 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_bar_source")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_bar_source (Phase 223/224)"
        }
        $scanLabelBarSource = $summary.most_recent_labeled_outcome_label_bar_source
        $scanLabelBarSourcePart = if ($null -eq $scanLabelBarSource -or $scanLabelBarSource -eq "") { "null" } else { [string]$scanLabelBarSource }
        Write-Host "OK  Phase 224 most_recent_labeled_outcome_label_bar_source=$scanLabelBarSourcePart"
        # Phase 226: most_recent_labeled_outcome_label_computed_at from Phase 225 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_computed_at")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_computed_at (Phase 225/226)"
        }
        $scanLabelComputedAt = $summary.most_recent_labeled_outcome_label_computed_at
        $scanLabelComputedAtPart = if ($null -eq $scanLabelComputedAt -or $scanLabelComputedAt -eq "") { "null" } else { [string]$scanLabelComputedAt }
        Write-Host "OK  Phase 226 most_recent_labeled_outcome_label_computed_at=$scanLabelComputedAtPart"
        # Phase 228: most_recent_labeled_outcome_label_as_of_trading_date from Phase 227 (null OK when no scan labels).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_as_of_trading_date")) {
            throw "evidence-summary missing most_recent_labeled_outcome_label_as_of_trading_date (Phase 227/228)"
        }
        $scanLabelAsOf = $summary.most_recent_labeled_outcome_label_as_of_trading_date
        $scanLabelAsOfPart = if ($null -eq $scanLabelAsOf -or $scanLabelAsOf -eq "") { "null" } else { [string]$scanLabelAsOf }
        Write-Host "OK  Phase 228 most_recent_labeled_outcome_label_as_of_trading_date=$scanLabelAsOfPart"
        # Phase 230: scan_labeled_freshness_lag_trading_days from Phase 229 (null OK when either as_of missing).
        if (-not ($summary.PSObject.Properties.Name -contains "scan_labeled_freshness_lag_trading_days")) {
            throw "evidence-summary missing scan_labeled_freshness_lag_trading_days (Phase 229/230)"
        }
        $scanLag = $summary.scan_labeled_freshness_lag_trading_days
        $scanLagPart = if ($null -eq $scanLag -or $scanLag -eq "") { "null" } else { [string]$scanLag }
        Write-Host "OK  Phase 230 scan_labeled_freshness_lag_trading_days=$scanLagPart"
        # Phase 232: latest_assessment_is_label_ready from Phase 231 (null OK when no assessment).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_assessment_is_label_ready")) {
            throw "evidence-summary missing latest_assessment_is_label_ready (Phase 231/232)"
        }
        $labelReady = $summary.latest_assessment_is_label_ready
        # Do not treat $false as empty: in PowerShell `$false -eq ""` is $true.
        $labelReadyPart = if ($null -eq $labelReady) { "null" } else { [string]$labelReady }
        Write-Host "OK  Phase 232 latest_assessment_is_label_ready=$labelReadyPart"
        # Phase 234: latest_assessment_label_block_reason from Phase 233 (null OK when ready / no assessment).
        if (-not ($summary.PSObject.Properties.Name -contains "latest_assessment_label_block_reason")) {
            throw "evidence-summary missing latest_assessment_label_block_reason (Phase 233/234)"
        }
        $blockReason = $summary.latest_assessment_label_block_reason
        $blockReasonPart = if ($null -eq $blockReason -or $blockReason -eq "") { "null" } else { [string]$blockReason }
        Write-Host "OK  Phase 234 latest_assessment_label_block_reason=$blockReasonPart"
        # Phase 236: most_recent_labelable_as_of_trading_date from Phase 235 (null OK when none label-ready).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_labelable_as_of_trading_date")) {
            throw "evidence-summary missing most_recent_labelable_as_of_trading_date (Phase 235/236)"
        }
        $labelableAsOf = $summary.most_recent_labelable_as_of_trading_date
        $labelableAsOfPart = if ($null -eq $labelableAsOf -or $labelableAsOf -eq "") { "null" } else { [string]$labelableAsOf }
        Write-Host "OK  Phase 236 most_recent_labelable_as_of_trading_date=$labelableAsOfPart"
        # Phase 238: most_recent_unlabeled_labelable_as_of_trading_date from Phase 237 (null OK when none).
        if (-not ($summary.PSObject.Properties.Name -contains "most_recent_unlabeled_labelable_as_of_trading_date")) {
            throw "evidence-summary missing most_recent_unlabeled_labelable_as_of_trading_date (Phase 237/238)"
        }
        $unlabeledLabelableAsOf = $summary.most_recent_unlabeled_labelable_as_of_trading_date
        $unlabeledLabelableAsOfPart = if ($null -eq $unlabeledLabelableAsOf -or $unlabeledLabelableAsOf -eq "") { "null" } else { [string]$unlabeledLabelableAsOf }
        Write-Host "OK  Phase 238 most_recent_unlabeled_labelable_as_of_trading_date=$unlabeledLabelableAsOfPart"
        # Phase 240: scan_unlabeled_label_ready_count from Phase 239 (0 OK when none).
        if (-not ($summary.PSObject.Properties.Name -contains "scan_unlabeled_label_ready_count")) {
            throw "evidence-summary missing scan_unlabeled_label_ready_count (Phase 239/240)"
        }
        $unlabeledReadyCount = $summary.scan_unlabeled_label_ready_count
        Write-Host "OK  Phase 240 scan_unlabeled_label_ready_count=$unlabeledReadyCount"
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
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_component_source")) {
            throw "evidence-summary/export missing latest_component_source (Phase 59/60)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_resolved_label_bar_source")) {
            throw "evidence-summary/export missing latest_resolved_label_bar_source (Phase 59/60)"
        }
        if ($null -eq $exportBody.mixed_component_source_assessment_count -or [int]$exportBody.mixed_component_source_assessment_count -lt 0) {
            throw "evidence-summary/export mixed_component_source_assessment_count must be >= 0"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "mixed_unlabeled_assessment_count")) {
            throw "evidence-summary/export missing mixed_unlabeled_assessment_count (Phase 67/68)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_mixed_label_bar_source")) {
            throw "evidence-summary/export missing latest_mixed_label_bar_source (Phase 67/68)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "mixed_labeled_assessment_count")) {
            throw "evidence-summary/export missing mixed_labeled_assessment_count (Phase 69/70)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "labeled_assessment_count")) {
            throw "evidence-summary/export missing labeled_assessment_count (Phase 145/146)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "unlabeled_assessment_count")) {
            throw "evidence-summary/export missing unlabeled_assessment_count (Phase 145/146)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_coverage_confidence")) {
            throw "evidence-summary/export missing latest_coverage_confidence (Phase 147/148)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_research_index")) {
            throw "evidence-summary/export missing latest_research_index (Phase 149/150)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_as_of_trading_date")) {
            throw "evidence-summary/export missing latest_as_of_trading_date (Phase 151/152)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_bar_count")) {
            throw "evidence-summary/export missing latest_bar_count (Phase 153/154)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_input_source")) {
            throw "evidence-summary/export missing latest_input_source (Phase 155/156)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_method_id")) {
            throw "evidence-summary/export missing latest_method_id (Phase 157/158)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_method_version")) {
            throw "evidence-summary/export missing latest_method_version (Phase 159/160)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_lookback_end_date")) {
            throw "evidence-summary/export missing latest_lookback_end_date (Phase 161/162)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_lookback_start_date")) {
            throw "evidence-summary/export missing latest_lookback_start_date (Phase 163/164)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_schema_version")) {
            throw "evidence-summary/export missing latest_schema_version (Phase 165/166)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_computed_at")) {
            throw "evidence-summary/export missing latest_computed_at (Phase 167/168)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_event_time")) {
            throw "evidence-summary/export missing latest_event_time (Phase 169/170)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_probability_confidence")) {
            throw "evidence-summary/export missing latest_probability_confidence (Phase 171/172)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_assessment_id")) {
            throw "evidence-summary/export missing latest_assessment_id (Phase 173/174)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_id")) {
            throw "evidence-summary/export missing latest_outcome_label_id (Phase 175/176)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_id")) {
            throw "evidence-summary/export missing latest_calibration_id (Phase 177/178)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_horizon_key")) {
            throw "evidence-summary/export missing latest_calibration_horizon_key (Phase 179/180)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_computed_at")) {
            throw "evidence-summary/export missing latest_calibration_computed_at (Phase 181/182)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_corpus_count")) {
            throw "evidence-summary/export missing latest_calibration_corpus_count (Phase 183/184)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_bucket_count")) {
            throw "evidence-summary/export missing latest_calibration_bucket_count (Phase 185/186)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_method_id")) {
            throw "evidence-summary/export missing latest_calibration_method_id (Phase 187/188)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_method_version")) {
            throw "evidence-summary/export missing latest_calibration_method_version (Phase 189/190)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_schema_version")) {
            throw "evidence-summary/export missing latest_calibration_schema_version (Phase 191/192)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_state")) {
            throw "evidence-summary/export missing latest_calibration_state (Phase 193/194)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_probability_confidence")) {
            throw "evidence-summary/export missing latest_calibration_probability_confidence (Phase 195/196)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_calibration_assessment_snapshot_id")) {
            throw "evidence-summary/export missing latest_calibration_assessment_snapshot_id (Phase 197/198)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_computed_at")) {
            throw "evidence-summary/export missing latest_outcome_label_computed_at (Phase 199/200)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_method_id")) {
            throw "evidence-summary/export missing latest_outcome_label_method_id (Phase 201/202)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_method_version")) {
            throw "evidence-summary/export missing latest_outcome_label_method_version (Phase 203/204)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_schema_version")) {
            throw "evidence-summary/export missing latest_outcome_label_schema_version (Phase 205/206)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_state")) {
            throw "evidence-summary/export missing latest_outcome_label_state (Phase 207/208)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_bar_source")) {
            throw "evidence-summary/export missing latest_outcome_label_bar_source (Phase 209/210)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_outcome_label_as_of_trading_date")) {
            throw "evidence-summary/export missing latest_outcome_label_as_of_trading_date (Phase 211/212)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_id")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_id (Phase 213/214)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_method_id")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_method_id (Phase 215/216)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_method_version")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_method_version (Phase 217/218)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_schema_version")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_schema_version (Phase 219/220)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_state")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_state (Phase 221/222)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_bar_source")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_bar_source (Phase 223/224)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_computed_at")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_computed_at (Phase 225/226)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label_as_of_trading_date")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label_as_of_trading_date (Phase 227/228)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "scan_labeled_freshness_lag_trading_days")) {
            throw "evidence-summary/export missing scan_labeled_freshness_lag_trading_days (Phase 229/230)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_assessment_is_label_ready")) {
            throw "evidence-summary/export missing latest_assessment_is_label_ready (Phase 231/232)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "latest_assessment_label_block_reason")) {
            throw "evidence-summary/export missing latest_assessment_label_block_reason (Phase 233/234)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labelable_as_of_trading_date")) {
            throw "evidence-summary/export missing most_recent_labelable_as_of_trading_date (Phase 235/236)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_unlabeled_labelable_as_of_trading_date")) {
            throw "evidence-summary/export missing most_recent_unlabeled_labelable_as_of_trading_date (Phase 237/238)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "scan_unlabeled_label_ready_count")) {
            throw "evidence-summary/export missing scan_unlabeled_label_ready_count (Phase 239/240)"
        }
        if ($null -eq $exportBody.calibration_readiness -or $null -eq $exportBody.calibration_readiness.by_horizon) {
            throw "evidence-summary/export.calibration_readiness missing by_horizon (Phase 75)"
        }
        $exportHorizonKeys = @(
            $exportBody.calibration_readiness.by_horizon | ForEach-Object { [string]$_.outcome_horizon_key }
        )
        foreach ($required in @("forward_return_5", "forward_return_20")) {
            if ($exportHorizonKeys -notcontains $required) {
                throw ("evidence-summary/export.calibration_readiness.by_horizon missing {0}" -f $required)
            }
        }
        foreach ($field in @("corpus_count", "bucket_count")) {
            if (-not ($exportBody.calibration_readiness.PSObject.Properties.Name -contains $field)) {
                throw "evidence-summary/export.calibration_readiness missing $field (Phase 76)"
            }
            if ($null -eq $exportBody.calibration_readiness.$field -or [int]$exportBody.calibration_readiness.$field -lt 0) {
                throw "evidence-summary/export.calibration_readiness.$field must be >= 0 (Phase 76)"
            }
        }
        foreach ($field in @("min_corpus", "min_bucket")) {
            if (-not ($exportBody.calibration_readiness.PSObject.Properties.Name -contains $field)) {
                throw "evidence-summary/export.calibration_readiness missing $field (Phase 76)"
            }
            if ($null -eq $exportBody.calibration_readiness.$field -or [int]$exportBody.calibration_readiness.$field -lt 1) {
                throw "evidence-summary/export.calibration_readiness.$field must be >= 1 (Phase 76)"
            }
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_assessment_id")) {
            throw "evidence-summary/export missing most_recent_labeled_assessment_id (Phase 79/80)"
        }
        if (-not ($exportBody.PSObject.Properties.Name -contains "most_recent_labeled_outcome_label")) {
            throw "evidence-summary/export missing most_recent_labeled_outcome_label (Phase 79/80)"
        }
        Write-Host "OK  evidence-summary/export attachment state=research_only assessments=$($exportBody.assessment_count) provenance fields present"
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
out=`$(docker compose $composeFileArgs --env-file .env.nas --project-directory . exec -T backend alembic current 2>&1)
echo "`$out"
echo "`$out" | grep -E '0009|head' >/dev/null
"@
    & ssh @sshArgs $remote $cmd
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic current did not report migration 0009 / head. Apply alembic upgrade head on the NAS."
    }
    Write-Host "OK  alembic current includes 0009 / head"

    Write-Host "==> Phase 52 research bar load setting (via SSH)"
    $barLoadCmd = @"
set -euo pipefail
cd '$dir'
if grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=[0-9]+' .env.nas >/dev/null; then
  grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=' .env.nas
else
  echo 'AEGIS_RESEARCH_BAR_LOAD_LIMIT missing from .env.nas' >&2
  exit 1
fi
val=`$(grep -E '^AEGIS_RESEARCH_BAR_LOAD_LIMIT=' .env.nas | head -n1 | cut -d= -f2)
if [ "`$val" -lt 40 ] || [ "`$val" -gt 2000 ]; then
  echo "AEGIS_RESEARCH_BAR_LOAD_LIMIT out of bounds: `$val" >&2
  exit 1
fi
"@
    & ssh @sshArgs $remote $barLoadCmd
    if ($LASTEXITCODE -ne 0) {
        throw "Phase 52: AEGIS_RESEARCH_BAR_LOAD_LIMIT missing or out of bounds on NAS .env.nas (ADR-0053)."
    }
    Write-Host "OK  AEGIS_RESEARCH_BAR_LOAD_LIMIT present on NAS .env.nas"

    Write-Host "==> Phase 54 daily bar output size (via SSH)"
    # Avoid parentheses in remote echo text: OpenSSH on Windows wraps remote cmds in
    # bash -c, and unquoted (...) tokens break the remote script parse.
    $outputSizeCmd = @"
set -euo pipefail
cd '$dir'
if grep -E '^AEGIS_DAILY_BAR_OUTPUT_SIZE=full' .env.nas >/dev/null; then
  grep -E '^AEGIS_DAILY_BAR_OUTPUT_SIZE=' .env.nas
else
  echo 'AEGIS_DAILY_BAR_OUTPUT_SIZE must be full on .env.nas' >&2
  exit 1
fi
"@
    & ssh @sshArgs $remote $outputSizeCmd
    if ($LASTEXITCODE -ne 0) {
        throw "Phase 54: AEGIS_DAILY_BAR_OUTPUT_SIZE must be full on NAS .env.nas (ADR-0055)."
    }
    Write-Host "OK  AEGIS_DAILY_BAR_OUTPUT_SIZE=full on NAS .env.nas"

    Write-Host "==> Phase 56 research cross-source fill (via SSH)"
    $crossFillCmd = @"
set -euo pipefail
cd '$dir'
if grep -E '^AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true' .env.nas >/dev/null; then
  grep -E '^AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=' .env.nas
else
  echo 'AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL must be true on .env.nas' >&2
  exit 1
fi
"@
    & ssh @sshArgs $remote $crossFillCmd
    if ($LASTEXITCODE -ne 0) {
        throw "Phase 56: AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL must be true on NAS .env.nas (ADR-0057)."
    }
    Write-Host "OK  AEGIS_RESEARCH_ALLOW_CROSS_SOURCE_COMPONENT_FILL=true on NAS .env.nas"

    if (Test-NasTlsEnabled) {
        Write-Host "==> Caddy service (TLS profile)"
        $caddyCmd = @"
set -euo pipefail
cd '$dir'
docker compose $composeFileArgs --env-file .env.nas --project-directory . ps --status running caddy | grep -E 'caddy' >/dev/null
"@
        & ssh @sshArgs $remote $caddyCmd
        if ($LASTEXITCODE -ne 0) {
            throw "TLS profile enabled but caddy service is not running."
        }
        Write-Host "OK  caddy service is running"
    }

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
