# Registra verificacao automatica no Agendador de Tarefas (Windows).
$ErrorActionPreference = "Stop"

$ps1 = (Resolve-Path (Join-Path $PSScriptRoot "executar_notificacoes.ps1")).Path
$nomeTarefa = "StudyHub Notificacoes Telegram"
$intervaloMinutos = 15

$existente = Get-ScheduledTask -TaskName $nomeTarefa -ErrorAction SilentlyContinue
if ($existente) {
    Write-Host "Removendo agendamento anterior..."
    Unregister-ScheduledTask -TaskName $nomeTarefa -Confirm:$false
}

$acao = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps1`""

$gatilho = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $intervaloMinutos) `
    -RepetitionDuration (New-TimeSpan -Days 3650)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $nomeTarefa `
    -Action $acao `
    -Trigger $gatilho `
    -Principal $principal `
    -Description "Verifica tarefas do StudyHub e envia lembretes pelo Telegram" | Out-Null

Write-Host "Tarefa '$nomeTarefa' criada (a cada $intervaloMinutos min)."
Write-Host "Log: backend\logs\notificacoes_agendador.log"
Write-Host "Testar: Start-ScheduledTask -TaskName '$nomeTarefa'"
