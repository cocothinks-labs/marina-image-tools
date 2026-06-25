@echo off
chcp 65001 >nul
title Remove BG — Eliminador de fondos IA
python "%~dp0remove_bg.py" %*
if %errorlevel% neq 0 pause
