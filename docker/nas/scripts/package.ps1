<#
.SYNOPSIS
  Build linux/amd64 images and stage a transferrable NAS package (Phase 7 + optional Phase 9 TLS).

.DESCRIPTION
  Requires a filled `.env.nas` at the repository root (copy from `.env.nas.example`).
  Does not connect to any NAS. Upload is a separate deploy step; verify is mandatory after deploy.
  When AEGIS_NAS_TLS_ENABLED=true, fails closed without TLS material and stages the Caddy overlay.

.EXAMPLE
  .\docker\nas\scripts\package.ps1
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "_common.ps1")

$RepoRoot = Get-RepoRoot -ScriptDir $ScriptDir
$EnvNas = Join-Path $RepoRoot ".env.nas"
Import-DotEnvFile -Path $EnvNas
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

$DistDir = Join-Path $RepoRoot "docker\nas\dist"
$PackageDir = Join-Path $DistDir "aegis-nas-package"
$ImagesTar = Join-Path $PackageDir "images\aegis-images-amd64.tar"

if (Test-Path -LiteralPath $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
}
New-Item -ItemType Directory -Path (Join-Path $PackageDir "images") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "docker\nas\scripts") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "docker\nas\proxy\certs") -Force | Out-Null

$composeArgs = Get-ComposeNasArgs -RepoRoot $RepoRoot

Write-Host "==> Validating NAS Compose overlay"
& docker compose @composeArgs config --quiet
if ($LASTEXITCODE -ne 0) { throw "docker compose config failed" }

Write-Host "==> Building linux/amd64 images (backend + frontend)"
& docker compose @composeArgs build --pull
if ($LASTEXITCODE -ne 0) { throw "docker compose build failed" }

Write-Host "==> Resolving image names for docker save"
$images = & docker compose @composeArgs config --images
if ($LASTEXITCODE -ne 0) { throw "docker compose config --images failed" }
$imageList = @($images | Where-Object { $_ -and $_.Trim() -ne "" })
if ($imageList.Count -lt 2) {
    throw "Expected at least backend and frontend images; got: $($imageList -join ', ')"
}

Write-Host "==> Saving images to $ImagesTar"
& docker save -o $ImagesTar @imageList
if ($LASTEXITCODE -ne 0) { throw "docker save failed" }

Write-Host "==> Staging package files"
Copy-Item (Join-Path $RepoRoot "docker-compose.yml") (Join-Path $PackageDir "docker-compose.yml")
New-Item -ItemType Directory -Path (Join-Path $PackageDir "docker\nas") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml") (Join-Path $PackageDir "docker\nas\docker-compose.nas.yml")
Copy-Item (Join-Path $RepoRoot "docker\nas\docker-compose.nas.tls.yml") (Join-Path $PackageDir "docker\nas\docker-compose.nas.tls.yml")
Copy-Item (Join-Path $RepoRoot "docker\nas\README.md") (Join-Path $PackageDir "docker\nas\README.md")
Copy-Item (Join-Path $RepoRoot ".env.nas.example") (Join-Path $PackageDir ".env.nas.example")
Copy-Item (Join-Path $RepoRoot "docker\nas\scripts\*") (Join-Path $PackageDir "docker\nas\scripts\") -Recurse
Copy-Item (Join-Path $RepoRoot "docker\nas\proxy\Caddyfile.files") (Join-Path $PackageDir "docker\nas\proxy\Caddyfile.files")
Copy-Item (Join-Path $RepoRoot "docker\nas\proxy\Caddyfile.acme") (Join-Path $PackageDir "docker\nas\proxy\Caddyfile.acme")
Copy-Item (Join-Path $RepoRoot "docker\nas\proxy\README.md") (Join-Path $PackageDir "docker\nas\proxy\README.md")
Copy-Item (Join-Path $RepoRoot "docker\nas\proxy\certs\README.md") (Join-Path $PackageDir "docker\nas\proxy\certs\README.md")
Copy-Item (Join-Path $RepoRoot "docker\nas\proxy\certs\.gitkeep") (Join-Path $PackageDir "docker\nas\proxy\certs\.gitkeep")

$ArchivePath = Join-Path $DistDir "aegis-nas-package.zip"
if (Test-Path -LiteralPath $ArchivePath) {
    Remove-Item -LiteralPath $ArchivePath -Force
}
Compress-Archive -Path (Join-Path $PackageDir "*") -DestinationPath $ArchivePath -Force

Write-Host ""
Write-Host "Package ready:"
Write-Host "  Directory: $PackageDir"
Write-Host "  Archive:   $ArchivePath"
if (Test-NasTlsEnabled) {
    Write-Host "  TLS:       enabled (Caddy overlay included; ensure PEMs or ACME on the NAS)"
}
Write-Host ""
Write-Host "Next: run deploy.ps1 (transfer + start). Upload alone is NOT a verified deployment;"
Write-Host "      run verify.ps1 after the stack is up."
