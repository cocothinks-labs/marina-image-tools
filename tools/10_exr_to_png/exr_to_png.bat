@echo off
chcp 65001 >nul
title EXR to PNG — Conversor EXR 32-bit
python "%~dp0exr_to_png.py" %*
if %errorlevel% neq 0 pause
