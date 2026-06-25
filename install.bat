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
    echo  Marca "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo  [1/2] Instalando dependencias base ^(Pillow, rembg, imagehash^)...
pip install "Pillow>=10.0" "rembg>=2.0" "onnxruntime>=1.16" "imagehash>=4.3" -q
if %errorlevel% neq 0 (
    echo  ERROR al instalar dependencias base. Revisa la salida anterior.
    pause
    exit /b 1
)
echo  Dependencias base OK.
echo.

echo  [2/2] Instalando MediaPipe ^(Google^) para auto-encuadre inteligente...
echo  Primera descarga: ~100MB. Por favor espera...
echo.
pip install "mediapipe>=0.10" "opencv-python>=4.8" -q
if %errorlevel% neq 0 (
    echo  ADVERTENCIA: MediaPipe no se instalo correctamente.
    echo  Las herramientas Social Resize y Video Social Resize funcionaran
    echo  con encuadre centrado en lugar de auto-encuadre por cara.
    echo  Puedes intentar instalarlo manualmente: pip install mediapipe
) else (
    echo  MediaPipe ^(auto-encuadre^) instalado correctamente.
)

echo.
echo  ============================================
echo   Instalacion completada.
echo   Ejecuta create_shortcuts.ps1 en PowerShell
echo   para crear los iconos en el Escritorio:
echo     powershell -ExecutionPolicy Bypass -File .\create_shortcuts.ps1
echo  ============================================
echo.
pause
