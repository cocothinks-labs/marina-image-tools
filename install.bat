@echo off
chcp 65001 >nul
title Instalador — Marina Image Tools

echo.
echo  ============================================
echo   MARINA IMAGE TOOLS — Instalador
echo  ============================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python no encontrado.
    echo  Descargalo de https://www.python.org/downloads/
    echo  y asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo  Instalando dependencias Python...
echo.
pip install -r "%~dp0requirements.txt"

if %errorlevel% neq 0 (
    echo.
    echo  ERROR al instalar dependencias. Revisa la salida anterior.
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   Instalacion completada correctamente.
echo   Ejecuta create_shortcuts.ps1 en PowerShell
echo   para crear los iconos en el escritorio.
echo  ============================================
echo.
pause
