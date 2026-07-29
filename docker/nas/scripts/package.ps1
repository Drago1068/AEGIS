<#
.SYNOPSIS
  Build NAS-target images and stage a transferrable package (Phase 7 + optional Phase 9 TLS).

.DESCRIPTION
  Requires a filled `.env.nas` at the repository root (copy from `.env.nas.example`).
  Does not connect to any NAS. Upload is a separate deploy step; verify is mandatory after deploy.
  When AEGIS_NAS_TLS_ENABLED=true, fails closed without TLS material and stages the Caddy overlay.
  Image platform comes from AEGIS_NAS_PLATFORM (default linux/amd64; use linux/arm64 on aarch64 NAS).

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
$platform = [Environment]::GetEnvironmentVariable("AEGIS_NAS_PLATFORM")
if ([string]::IsNullOrWhiteSpace($platform)) { $platform = "linux/amd64" }
# Keep historical filename for deploy script compatibility; contents match AEGIS_NAS_PLATFORM.
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

Write-Host "==> Building $platform images (backend + frontend)"
$env:DOCKER_DEFAULT_PLATFORM = $platform
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

# Skip Compress-Archive: large image tars routinely hang Windows Compress-Archive.
# deploy.ps1 uses the package directory, not the zip.

Write-Host ""
Write-Host "Package ready:"
Write-Host "  Directory: $PackageDir"
Write-Host "  Platform:  $platform"
Write-Host "  Images:    $ImagesTar"
if (Test-NasTlsEnabled) {
    Write-Host "  TLS:       enabled (Caddy overlay included; ensure PEMs or ACME on the NAS)"
}
Write-Host ""
Write-Host "Next: run deploy.ps1 (transfer + start). Upload alone is NOT a verified deployment;"
Write-Host "      run verify.ps1 after the stack is up."
