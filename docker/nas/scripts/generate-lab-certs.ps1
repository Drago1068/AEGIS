<#
.SYNOPSIS
  Generate self-signed lab PEMs for Phase 40 NAS TLS cutover (ADR-0041).

.DESCRIPTION
  Writes frontend.crt/.key and api.crt/.key under docker/nas/proxy/certs/ for
  aegis.local and api.aegis.local. Never commit these files (gitignored).

.EXAMPLE
  .\docker\nas\scripts\generate-lab-certs.ps1
#>
param(
    [string]$FrontendHost = "aegis.local",
    [string]$ApiHost = "api.aegis.local",
    [int]$Days = 825
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$CertsDir = Join-Path $RepoRoot "docker\nas\proxy\certs"

$opensslCmd = Get-Command openssl -ErrorAction SilentlyContinue
$opensslPath = $null
if ($opensslCmd) {
    $opensslPath = $opensslCmd.Source
} else {
    $candidates = @(
        "C:\Program Files\Git\usr\bin\openssl.exe",
        "C:\Program Files\OpenSSL-Win64\bin\openssl.exe",
        (Join-Path $env:LOCALAPPDATA "Programs\Git\usr\bin\openssl.exe")
    )
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) {
            $opensslPath = $c
            break
        }
    }
}
if (-not $opensslPath) {
    throw "openssl not found on PATH. Install OpenSSL (or Git for Windows) and retry."
}

New-Item -ItemType Directory -Force -Path $CertsDir | Out-Null

function New-LabCert {
    param(
        [Parameter(Mandatory = $true)][string]$CommonName,
        [Parameter(Mandatory = $true)][string]$OutPrefix
    )
    $keyPath = Join-Path $CertsDir "$OutPrefix.key"
    $crtPath = Join-Path $CertsDir "$OutPrefix.crt"
    $cfgPath = Join-Path $CertsDir "$OutPrefix.openssl.cnf"
    @"
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = $CommonName

[v3_req]
subjectAltName = @alt_names
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = $CommonName
"@ | Set-Content -LiteralPath $cfgPath -Encoding ascii

    & $opensslPath req -x509 -nodes -newkey rsa:2048 `
        -keyout $keyPath -out $crtPath -days $Days -config $cfgPath
    if ($LASTEXITCODE -ne 0) {
        throw "openssl failed generating $OutPrefix cert for $CommonName"
    }
    Remove-Item -LiteralPath $cfgPath -Force -ErrorAction SilentlyContinue
    Write-Host "Wrote $crtPath and $keyPath (CN/SAN=$CommonName)"
}

New-LabCert -CommonName $FrontendHost -OutPrefix "frontend"
New-LabCert -CommonName $ApiHost -OutPrefix "api"
Write-Host "Lab PEMs ready under $CertsDir (gitignored - do not commit)."
