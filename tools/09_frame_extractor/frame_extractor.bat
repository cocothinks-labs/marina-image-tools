@echo off
chcp 65001 >nul
title Frame Extractor — Extraer frames de vídeo
python "%~dp0frame_extractor.py" %*
if %errorlevel% neq 0 pause
