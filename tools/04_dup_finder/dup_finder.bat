@echo off
chcp 65001 >nul
title Dup Finder — Detector de duplicados
python "%~dp0dup_finder.py" %*
if %errorlevel% neq 0 pause
