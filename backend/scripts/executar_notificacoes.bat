@echo off
REM Executa uma verificacao de notificacoes Telegram (uso pelo Agendador de Tarefas).
setlocal
set "PROJETO=%~dp0..\.."
cd /d "%PROJETO%"
"%PROJETO%\venv\Scripts\python.exe" "%PROJETO%\backend\manage.py" verificar_notificacoes
