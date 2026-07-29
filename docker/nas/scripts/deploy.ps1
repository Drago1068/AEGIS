<#
.SYNOPSIS
  Transfer a NAS package over SSH/SCP, load images, start Compose, apply Alembic (Phase 7).

.DESCRIPTION
  Requires `.env.nas` with SSH and stack settings. A successful upload is NOT a verified
  deployment — run verify.ps1 afterward.

.EXAMPLE
  .\docker\nas\scripts\deploy.ps1
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "_common.ps1")

$RepoRoot = Get-RepoRoot -ScriptDir $ScriptDir
$EnvNas = Join-Path $RepoRoot ".env.nas"
Import-DotEnvFile -Path $EnvNas
Require-EnvVars -Names @(
    "AEGIS_NAS_SSH_HOST",
    "AEGIS_NAS_SSH_USER",
    "AEGIS_NAS_REMOTE_DIR",
    "AEGIS_OPERATOR_PASSWORD",
    "POSTGRES_PASSWORD",
    "NEXT_PUBLIC_API_BASE_URL",
    "AEGIS_CORS_ORIGINS"
)
Assert-NasSecretsNotPlaceholders

$hostName = $env:AEGIS_NAS_SSH_HOST
if ($hostName -match "^(replace-with-|your-)") {
    throw "AEGIS_NAS_SSH_HOST still looks like a placeholder. Set a real SSH host in .env.nas."
}

$PackageDir = Join-Path $RepoRoot "docker\nas\dist\aegis-nas-package"
$ImagesTar = Join-Path $PackageDir "images\aegis-images-amd64.tar"
if (-not (Test-Path -LiteralPath $ImagesTar)) {
    throw "Package images missing at $ImagesTar. Run package.ps1 first."
}

$remote = "{0}@{1}" -f $env:AEGIS_NAS_SSH_USER, $env:AEGIS_NAS_SSH_HOST
$remoteDir = $env:AEGIS_NAS_REMOTE_DIR.TrimEnd("/")
$sshArgs = Get-SshArgs
$scpArgs = Get-ScpArgs

Write-Host "==> Ensuring remote directory exists: $remoteDir"
& ssh @sshArgs $remote "mkdir -p '$remoteDir/images' '$remoteDir/docker/nas/scripts'"
if ($LASTEXITCODE -ne 0) { throw "ssh mkdir failed" }

Write-Host "==> Copying package files (compose, scripts, images)"
$filesToCopy = @(
    @{ Local = (Join-Path $PackageDir "docker-compose.yml"); Remote = "$remote`:$remoteDir/docker-compose.yml" },
    @{ Local = (Join-Path $PackageDir "docker\nas\docker-compose.nas.yml"); Remote = "$remote`:$remoteDir/docker/nas/docker-compose.nas.yml" },
    @{ Local = (Join-Path $PackageDir "docker\nas\README.md"); Remote = "$remote`:$remoteDir/docker/nas/README.md" },
    @{ Local = $ImagesTar; Remote = "$remote`:$remoteDir/images/aegis-images-amd64.tar" },
    @{ Local = $EnvNas; Remote = "$remote`:$remoteDir/.env.nas" }
)
foreach ($item in $filesToCopy) {
    Write-Host "  scp $($item.Local)"
    & scp @scpArgs $item.Local $item.Remote
    if ($LASTEXITCODE -ne 0) { throw "scp failed for $($item.Local)" }
}

# Copy scripts directory
& scp @scpArgs -r (Join-Path $PackageDir "docker\nas\scripts") "$remote`:$remoteDir/docker/nas/"
if ($LASTEXITCODE -ne 0) { throw "scp scripts failed" }

$remoteCmd = @"
set -euo pipefail
cd '$remoteDir'
echo '==> Loading images'
docker load -i images/aegis-images-amd64.tar
echo '==> Starting NAS Compose stack'
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas --project-directory . up -d --no-build
echo '==> Waiting for backend container'
for i in `$(seq 1 60); do
  if docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas --project-directory . ps --status running | grep -q backend; then
    break
  fi
  sleep 2
done
echo '==> Applying Alembic migrations (through 0005 / head)'
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas --project-directory . exec -T backend alembic upgrade head
echo '==> Migration current revision'
docker compose -f docker-compose.yml -f docker/nas/docker-compose.nas.yml --env-file .env.nas --project-directory . exec -T backend alembic current
echo 'Deploy start finished. Upload/start is NOT verification — run verify next.'
"@

Write-Host "==> Remote load, start, and migrate"
& ssh @sshArgs $remote $remoteCmd
if ($LASTEXITCODE -ne 0) { throw "remote deploy failed" }

Write-Host ""
Write-Host "Deploy transfer and start completed."
Write-Host "IMPORTANT: This is not a verified deployment. Run:"
Write-Host "  .\docker\nas\scripts\verify.ps1"
