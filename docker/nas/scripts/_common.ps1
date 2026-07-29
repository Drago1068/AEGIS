# Shared helpers for AEGIS NAS PowerShell scripts (Phase 7).
# Dot-source from package.ps1 / deploy.ps1 / verify.ps1 / validate-local.ps1.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    param([string]$ScriptDir)
    return (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
}

function Import-DotEnvFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required env file not found: $Path"
    }
    Get-Content -LiteralPath $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        Set-Item -Path "Env:$name" -Value $value
    }
}

function Require-EnvVars {
    param([Parameter(Mandatory = $true)][string[]]$Names)
    $missing = @()
    foreach ($name in $Names) {
        $val = [Environment]::GetEnvironmentVariable($name)
        if ([string]::IsNullOrWhiteSpace($val)) {
            $missing += $name
        }
    }
    if ($missing.Count -gt 0) {
        throw "Missing required environment variable(s): $($missing -join ', ')"
    }
}

function Assert-NasSecretsNotPlaceholders {
    $password = [Environment]::GetEnvironmentVariable("AEGIS_OPERATOR_PASSWORD")
    $dbPassword = [Environment]::GetEnvironmentVariable("POSTGRES_PASSWORD")
    $forbiddenOperator = @(
        "change-me-before-non-local-use",
        "replace-with-strong-non-default-nas-operator-password",
        "aegis",
        "operator"
    )
    $forbiddenDb = @(
        "aegis",
        "replace-with-strong-non-default-nas-db-password"
    )
    if ($forbiddenOperator -contains $password) {
        throw "AEGIS_OPERATOR_PASSWORD must be a strong non-default value for NAS (not a template placeholder)."
    }
    if ($forbiddenDb -contains $dbPassword) {
        throw "POSTGRES_PASSWORD must be a strong non-default value for NAS (not a template placeholder)."
    }
}

function Get-ComposeNasArgs {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $envFile = Join-Path $RepoRoot ".env.nas"
    if (-not (Test-Path -LiteralPath $envFile)) {
        throw "Missing .env.nas at repo root. Copy .env.nas.example and fill placeholders."
    }
    return @(
        "-f", (Join-Path $RepoRoot "docker-compose.yml"),
        "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml"),
        "--env-file", $envFile,
        "--project-directory", $RepoRoot
    )
}

function Get-SshArgs {
    $sshArgs = @()
    $port = [Environment]::GetEnvironmentVariable("AEGIS_NAS_SSH_PORT")
    if ([string]::IsNullOrWhiteSpace($port)) { $port = "22" }
    $sshArgs += @("-p", $port)
    $identity = [Environment]::GetEnvironmentVariable("AEGIS_NAS_SSH_IDENTITY_FILE")
    if (-not [string]::IsNullOrWhiteSpace($identity)) {
        $sshArgs += @("-i", $identity)
    }
    $sshArgs += @("-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new")
    return $sshArgs
}

function Get-ScpArgs {
    $scpArgs = @()
    $port = [Environment]::GetEnvironmentVariable("AEGIS_NAS_SSH_PORT")
    if ([string]::IsNullOrWhiteSpace($port)) { $port = "22" }
    $scpArgs += @("-P", $port)
    $identity = [Environment]::GetEnvironmentVariable("AEGIS_NAS_SSH_IDENTITY_FILE")
    if (-not [string]::IsNullOrWhiteSpace($identity)) {
        $scpArgs += @("-i", $identity)
    }
    $scpArgs += @("-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new")
    return $scpArgs
}
