@echo off
chcp 65001 >nul
title Grid Maker — Hoja de referencia
python "%~dp0grid_maker.py" %*
if %errorlevel% neq 0 pause
