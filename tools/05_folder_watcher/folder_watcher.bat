@echo off
chcp 65001 >nul
title Folder Watcher — Organizador automático
python "%~dp0folder_watcher.py" %*
if %errorlevel% neq 0 pause
