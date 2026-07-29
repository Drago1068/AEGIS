<#
.SYNOPSIS
  Local dry-run for NAS packaging without a live NAS (Phase 7 + optional Phase 9 TLS).

.DESCRIPTION
  Validates the Compose overlay with `.env.nas.example` (or `.env.nas` if present).
  Pass -Tls to force the Phase 9 TLS overlay dry-run (or set AEGIS_NAS_TLS_ENABLED=true).
  Optionally builds linux/amd64 images when -BuildImages is passed.

.EXAMPLE
  .\docker\nas\scripts\validate-local.ps1
  .\docker\nas\scripts\validate-local.ps1 -Tls
  .\docker\nas\scripts\validate-local.ps1 -BuildImages
#>
param(
    [switch]$BuildImages,
    [switch]$Tls
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "_common.ps1")

$RepoRoot = Get-RepoRoot -ScriptDir $ScriptDir
$EnvFile = Join-Path $RepoRoot ".env.nas"
$UsingExample = $false
if (-not (Test-Path -LiteralPath $EnvFile)) {
    $EnvFile = Join-Path $RepoRoot ".env.nas.example"
    $UsingExample = $true
    Write-Host "NOTE: .env.nas not found; using .env.nas.example for config dry-run only."
}

Import-DotEnvFile -Path $EnvFile
if ($Tls) {
    $env:AEGIS_NAS_TLS_ENABLED = "true"
}

$baseComposeArgs = @(
    "-f", (Join-Path $RepoRoot "docker-compose.yml"),
    "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml"),
    "--env-file", $EnvFile,
    "--project-directory", $RepoRoot
)

Write-Host "==> docker compose config (NAS overlay)"
& docker compose @baseComposeArgs config --quiet
if ($LASTEXITCODE -ne 0) { throw "NAS overlay compose config failed" }
Write-Host "OK  compose config (base NAS overlay)"

if (Test-NasTlsEnabled) {
    Write-Host "==> TLS profile selected - validating material and TLS overlay config"
    if ($UsingExample) {
        Assert-TlsProfileReady -RepoRoot $RepoRoot -AllowExamplePlaceholders
    } else {
        Assert-TlsProfileReady -RepoRoot $RepoRoot
    }
    $tlsComposeArgs = @(
        "-f", (Join-Path $RepoRoot "docker-compose.yml"),
        "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml"),
        "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.tls.yml"),
        "--env-file", $EnvFile,
        "--project-directory", $RepoRoot
    )
    & docker compose @tlsComposeArgs config --quiet
    if ($LASTEXITCODE -ne 0) { throw "NAS TLS overlay compose config failed" }
    Write-Host "OK  compose config (NAS + TLS overlay)"
} else {
    Write-Host "Skipped TLS overlay (set AEGIS_NAS_TLS_ENABLED=true or pass -Tls to validate)."
}

if ($BuildImages) {
    if ($UsingExample) {
        throw "Refusing amd64 image build with .env.nas.example placeholders. Copy to .env.nas, set real non-default secrets and NEXT_PUBLIC_API_BASE_URL, then re-run with -BuildImages."
    }
    Require-EnvVars -Names @(
        "NEXT_PUBLIC_API_BASE_URL",
        "AEGIS_CORS_ORIGINS",
        "AEGIS_OPERATOR_PASSWORD",
        "POSTGRES_PASSWORD"
    )
    Assert-NasSecretsNotPlaceholders
    if (Test-NasTlsEnabled) {
        Assert-TlsProfileReady -RepoRoot $RepoRoot
    }
    Write-Host "==> Building linux/amd64 images (no push, no deploy)"
    $composeArgs = Get-ComposeNasArgs -RepoRoot $RepoRoot -EnvFile $EnvFile
    & docker compose @composeArgs build
    if ($LASTEXITCODE -ne 0) { throw "NAS overlay image build failed" }
    Write-Host "OK  amd64 build"
} else {
    Write-Host "Skipped image build (pass -BuildImages to build linux/amd64 locally)."
}

Write-Host ""
Write-Host "Local NAS packaging dry-run succeeded. No NAS was contacted."
