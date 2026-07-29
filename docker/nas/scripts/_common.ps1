# Shared helpers for AEGIS NAS PowerShell scripts (Phase 7 + optional Phase 9 TLS).
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

function Test-NasTlsEnabled {
    $v = [Environment]::GetEnvironmentVariable("AEGIS_NAS_TLS_ENABLED")
    if ([string]::IsNullOrWhiteSpace($v)) { return $false }
    return @("true", "1", "yes") -contains $v.Trim().ToLowerInvariant()
}

function Resolve-NasRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$RawPath
    )
    if ([System.IO.Path]::IsPathRooted($RawPath)) {
        return $RawPath
    }
    $trimmed = $RawPath.TrimStart('.', '\', '/')
    $trimmed = $trimmed -replace '^\\+', '' -replace '^/+', ''
    if ($trimmed -match '^[\\/]?docker[\\/]nas[\\/]') {
        return (Join-Path $RepoRoot ($trimmed -replace '/', '\'))
    }
    return (Join-Path (Join-Path $RepoRoot "docker\nas") ($trimmed -replace '/', '\'))
}

function Assert-TlsProfileReady {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [switch]$AllowExamplePlaceholders
    )

    Require-EnvVars -Names @("AEGIS_TLS_FRONTEND_HOST", "AEGIS_TLS_API_HOST", "AEGIS_TLS_MODE")

    $feHost = $env:AEGIS_TLS_FRONTEND_HOST
    $apiHost = $env:AEGIS_TLS_API_HOST
    if (-not $AllowExamplePlaceholders) {
        if ($feHost -match "^replace-with-" -or $apiHost -match "^replace-with-") {
            throw "AEGIS_TLS_FRONTEND_HOST / AEGIS_TLS_API_HOST still look like placeholders."
        }
    }

    $secure = "$($env:AEGIS_SESSION_COOKIE_SECURE)".Trim().ToLowerInvariant()
    if ($secure -ne "true" -and $secure -ne "1") {
        throw "TLS profile requires AEGIS_SESSION_COOKIE_SECURE=true (Secure cookies need HTTPS)."
    }

    $urlVars = @(
        "AEGIS_CORS_ORIGINS",
        "NEXT_PUBLIC_API_BASE_URL",
        "AEGIS_NAS_API_BASE_URL",
        "AEGIS_NAS_FRONTEND_BASE_URL"
    )
    foreach ($name in $urlVars) {
        $val = [Environment]::GetEnvironmentVariable($name)
        if ([string]::IsNullOrWhiteSpace($val)) { continue }
        if ($val.StartsWith("http://")) {
            throw "$name must use https:// when the TLS profile is enabled (got HTTP). Secure cookies will not be sent by browsers over plain HTTP."
        }
        if (-not $AllowExamplePlaceholders -and -not $val.StartsWith("https://")) {
            throw "$name must be an https:// origin when TLS is enabled."
        }
    }

    $mode = $env:AEGIS_TLS_MODE.Trim().ToLowerInvariant()
    switch ($mode) {
        "files" {
            if ([string]::IsNullOrWhiteSpace($env:AEGIS_TLS_CADDYFILE)) {
                $env:AEGIS_TLS_CADDYFILE = "./proxy/Caddyfile.files"
            }
            $certsDirRaw = $env:AEGIS_TLS_CERTS_DIR
            if ([string]::IsNullOrWhiteSpace($certsDirRaw)) { $certsDirRaw = "./proxy/certs" }
            $certsDir = Resolve-NasRelativePath -RepoRoot $RepoRoot -RawPath $certsDirRaw
            if ($AllowExamplePlaceholders) {
                Write-Host "NOTE: TLS files mode with example env - compose config only; PEM presence not enforced."
            } else {
                foreach ($f in @("frontend.crt", "frontend.key", "api.crt", "api.key")) {
                    $path = Join-Path $certsDir $f
                    if (-not (Test-Path -LiteralPath $path)) {
                        throw "TLS files mode missing $path. Provide operator PEMs or switch AEGIS_TLS_MODE=acme when network allows."
                    }
                }
            }
        }
        "acme" {
            if ([string]::IsNullOrWhiteSpace($env:AEGIS_TLS_CADDYFILE)) {
                $env:AEGIS_TLS_CADDYFILE = "./proxy/Caddyfile.acme"
            }
            Require-EnvVars -Names @("AEGIS_TLS_ACME_EMAIL")
            if (-not $AllowExamplePlaceholders -and $env:AEGIS_TLS_ACME_EMAIL -match "^replace-with-") {
                throw "AEGIS_TLS_ACME_EMAIL still looks like a placeholder."
            }
        }
        default {
            throw "AEGIS_TLS_MODE must be 'files' or 'acme' (got: $($env:AEGIS_TLS_MODE))."
        }
    }
}

function Get-ComposeNasArgs {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [string]$EnvFile = ""
    )
    if ([string]::IsNullOrWhiteSpace($EnvFile)) {
        $EnvFile = Join-Path $RepoRoot ".env.nas"
    }
    if (-not (Test-Path -LiteralPath $EnvFile)) {
        throw "Missing env file at $EnvFile. Copy .env.nas.example and fill placeholders."
    }
    $args = @(
        "-f", (Join-Path $RepoRoot "docker-compose.yml"),
        "-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.yml")
    )
    if (Test-NasTlsEnabled) {
        $args += @("-f", (Join-Path $RepoRoot "docker\nas\docker-compose.nas.tls.yml"))
    }
    $args += @(
        "--env-file", $EnvFile,
        "--project-directory", $RepoRoot
    )
    return $args
}

function Get-ComposeNasRemoteFileFlags {
    # Relative -f flags for remote SSH (cwd = package root).
    $flags = @("-f", "docker-compose.yml", "-f", "docker/nas/docker-compose.nas.yml")
    if (Test-NasTlsEnabled) {
        $flags += @("-f", "docker/nas/docker-compose.nas.tls.yml")
    }
    return $flags
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
    # Legacy SCP (-O): OpenSSH's default SFTP backend fails on some UGREEN NAS paths
    # with "dest open ... No such file or directory" even when the directory exists.
    $scpArgs += @("-O", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new")
    return $scpArgs
}
