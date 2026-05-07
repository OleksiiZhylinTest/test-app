@echo off
cd /d "%~dp0..\.."

::  run_all_checks.bat  —  local mirror of the full CI pipeline
::
::  Usage:
::    run_all_checks.bat                    run ALL stages (lint, unit, component,
::                                          windows, security, integration, e2e)
::    run_all_checks.bat --skip-integration skip integration tests
::    run_all_checks.bat --skip-e2e         skip E2E tests (needs Jira + browser)
::
::  Jira credentials are read from the .env file or environment variables.

if exist ".venv\Scripts\python.exe" (
    set PYTHON=.venv\Scripts\python.exe
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not on PATH.
        pause
        exit /b 1
    )
    set PYTHON=python
)

%PYTHON% tests\runners\run_all_checks.py %*
set EXIT_CODE=%ERRORLEVEL%
pause
exit /b %EXIT_CODE%
