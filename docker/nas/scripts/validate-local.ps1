<#
.SYNOPSIS
  Local dry-run for NAS packaging without a live NAS (Phase 7).

.DESCRIPTION
  Validates the Compose overlay with `.env.nas.example` (or `.env.nas` if present).
  Optionally builds linux/amd64 images when -BuildImages is passed.

.EXAMPLE
  .\docker\nas\scripts\validate-local.ps1
  .\docker\nas\scripts\validate-local.ps1 -BuildImages
#>
param(
    [switch]$BuildImages
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

# For config dry-run with the example file, Compose required-var interpolation still needs
# values present; the example file supplies placeholders (sufficient for `config`, not deploy).
$composeArgs = @(
    "-f", (Join-Path $RepoRoot "docker-compose.yml"),
    "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml"),
    "--env-file", $EnvFile,
    "--project-directory", $RepoRoot
)

Write-Host "==> docker compose config (NAS overlay)"
& docker compose @composeArgs config --quiet
if ($LASTEXITCODE -ne 0) { throw "NAS overlay compose config failed" }
Write-Host "OK  compose config"

if ($BuildImages) {
    if ($UsingExample) {
        throw "Refusing amd64 image build with .env.nas.example placeholders. Copy to .env.nas, set real non-default secrets and NEXT_PUBLIC_API_BASE_URL, then re-run with -BuildImages."
    }
    Import-DotEnvFile -Path $EnvFile
    Require-EnvVars -Names @(
        "NEXT_PUBLIC_API_BASE_URL",
        "AEGIS_CORS_ORIGINS",
        "AEGIS_OPERATOR_PASSWORD",
        "POSTGRES_PASSWORD"
    )
    Assert-NasSecretsNotPlaceholders
    Write-Host "==> Building linux/amd64 images (no push, no deploy)"
    & docker compose @composeArgs build
    if ($LASTEXITCODE -ne 0) { throw "NAS overlay image build failed" }
    Write-Host "OK  amd64 build"
} else {
    Write-Host "Skipped image build (pass -BuildImages to build linux/amd64 locally)."
}

Write-Host ""
Write-Host "Local NAS packaging dry-run succeeded. No NAS was contacted."
