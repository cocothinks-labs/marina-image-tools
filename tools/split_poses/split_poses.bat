@echo off
chcp 65001 >nul
title Split Poses — Separador de poses
python "%~dp0split_poses.py" %*
if %errorlevel% neq 0 pause
