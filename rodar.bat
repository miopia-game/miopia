@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; sys.exit(not ((3, 10) <= sys.version_info[:2] <= (3, 14)))" >nul 2>&1
    if not errorlevel 1 (
        ".venv\Scripts\python.exe" "%~dp0tools\preparar.py" %*
        if errorlevel 1 goto :falhou
        exit /b 0
    )
)
for %%V in (3.14 3.13 3.12 3.11 3.10) do (
    py -%%V -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        py -%%V "%~dp0tools\preparar.py" %*
        if errorlevel 1 goto :falhou
        exit /b 0
    )
)
python -c "import sys; sys.exit(not ((3, 10) <= sys.version_info[:2] <= (3, 14)))" >nul 2>&1
if errorlevel 1 (
    echo Instale Python 3.10 a 3.14 para usar a pasta de desenvolvimento.
    goto :falhou
)
python "%~dp0tools\preparar.py" %*
if not errorlevel 1 exit /b 0
:falhou
pause
exit /b 1
