<#
  Lê um segredo no AWS Secrets Manager e grava .env.secrets.local para usar com Docker Compose.

  Pré-requisitos: AWS CLI v2 autenticado (aws configure, SSO ou variáveis de ambiente).

  Segredo no formato texto puro: o valor inteiro vira OPENAI_API_KEY.
  Segredo JSON: exporta cada propriedade com nome em MAIÚSCULAS (ex.: OPENAI_API_KEY, AI_MODEL).

  Uso:
    .\scripts\fetch-secrets.ps1 -SecretId "leitor-nf-ia/dev"
    $env:AWS_SECRET_ID = "leitor-nf-ia/dev"; .\scripts\fetch-secrets.ps1

  Depois: docker compose up --build
#>
param(
    [Parameter(Mandatory = $false)]
    [string] $SecretId = $env:AWS_SECRET_ID,

    [string] $Region = $(if ($env:AWS_DEFAULT_REGION) { $env:AWS_DEFAULT_REGION } elseif ($env:AWS_REGION) { $env:AWS_REGION } else { "" }),

    [string] $OutFile = ".env.secrets.local",

    [string] $Profile,

    [switch] $DryRun
)

$ErrorActionPreference = "Stop"

if (-not $SecretId) {
    Write-Error "Indique -SecretId ou defina a variável de ambiente AWS_SECRET_ID."
    exit 1
}

$awsCmd = Get-Command aws -ErrorAction SilentlyContinue
if (-not $awsCmd) {
    Write-Error "AWS CLI não encontrado no PATH. Instale: https://aws.amazon.com/cli/"
    exit 1
}

$awsArgs = @(
    "secretsmanager", "get-secret-value",
    "--secret-id", $SecretId,
    "--query", "SecretString",
    "--output", "text"
)
if ($Region) {
    $awsArgs += @("--region", $Region)
}
if ($Profile) {
    $awsArgs += @("--profile", $Profile)
}

$raw = & aws @awsArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Falha ao ler o segredo (aws secretsmanager get-secret-value). Verifique credenciais e IAM (secretsmanager:GetSecretValue)."
    exit $LASTEXITCODE
}

$t = $raw.Trim()
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Gerado por scripts/fetch-secrets.ps1 — não commitar (está no .gitignore)")
$lines.Add("# SecretId: $SecretId")

if ($t.StartsWith("{")) {
    try {
        $obj = $t | ConvertFrom-Json
    } catch {
        Write-Error "Segredo JSON inválido: $_"
        exit 1
    }
    foreach ($prop in $obj.PSObject.Properties) {
        $name = $prop.Name
        $val = $prop.Value
        if ($null -eq $val) { continue }
        if ($val -is [string] -or $val -is [int] -or $val -is [long] -or $val -is [double] -or $val -is [bool]) {
            if ($name -cmatch '^[A-Z][A-Z0-9_]*$') {
                $lines.Add("${name}=$val")
            }
        }
    }
    $hasKey = $lines | Where-Object { $_ -match '^OPENAI_API_KEY=' }
    if (-not $hasKey) {
        Write-Error "JSON sem propriedade OPENAI_API_KEY (maiúsculas). Chaves esperadas: OPENAI_API_KEY, opcionalmente AI_MODEL, etc."
        exit 1
    }
} else {
    $lines.Add("OPENAI_API_KEY=$t")
}

$body = ($lines -join "`n") + "`n"
$fullPath = Join-Path (Get-Location) $OutFile
$dir = Split-Path -Parent $fullPath
if ($dir -and -not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

if ($DryRun) {
    Write-Host $body
    exit 0
}

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($fullPath, $body, $utf8NoBom)
Write-Host "Escrito $fullPath"
