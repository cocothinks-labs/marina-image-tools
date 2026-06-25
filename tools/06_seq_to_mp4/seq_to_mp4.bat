@echo off
chcp 65001 >nul
title Seq to MP4 — Secuencia a vídeo
python "%~dp0seq_to_mp4.py" %*
if %errorlevel% neq 0 pause
