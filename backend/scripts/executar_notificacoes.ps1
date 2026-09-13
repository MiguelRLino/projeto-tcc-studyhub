# Verifica notificacoes Telegram (Agendador de Tarefas / execucao manual).
$ErrorActionPreference = "Stop"

$projeto = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$python = Join-Path $projeto "venv\Scripts\python.exe"
$manage = Join-Path $projeto "backend\manage.py"
$logDir = Join-Path $projeto "backend\logs"
$logFile = Join-Path $logDir "notificacoes_agendador.log"

if (-not (Test-Path $python)) {
    throw "Python nao encontrado: $python"
}
if (-not (Test-Path $manage)) {
    throw "manage.py nao encontrado: $manage"
}
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$linha = "`n===== $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====="
Add-Content -Path $logFile -Value $linha

Push-Location (Join-Path $projeto "backend")
try {
    $saida = & $python $manage verificar_notificacoes 2>&1 | Out-String
    Add-Content -Path $logFile -Value $saida -Encoding utf8
    Write-Output $saida
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
