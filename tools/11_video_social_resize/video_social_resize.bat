@echo off
chcp 65001 >nul
title Video Social Resize — Exportar vídeo a redes sociales
python "%~dp0video_social_resize.py" %*
if %errorlevel% neq 0 pause
