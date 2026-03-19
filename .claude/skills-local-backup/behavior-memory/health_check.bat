@echo off
setlocal

set "SCRIPT=%USERPROFILE%\.behavior-memory\health_check.py"

if not exist "%SCRIPT%" (
  echo health check script not found: %SCRIPT%
  exit /b 1
)

python "%SCRIPT%" --full
exit /b %ERRORLEVEL%
