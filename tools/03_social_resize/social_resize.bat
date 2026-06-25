@echo off
chcp 65001 >nul
title Social Resize — Exportar a redes sociales
python "%~dp0social_resize.py" %*
if %errorlevel% neq 0 pause
