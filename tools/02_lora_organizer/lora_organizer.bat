@echo off
chcp 65001 >nul
title LoRA Organizer — Dataset para LoRA
python "%~dp0lora_organizer.py" %*
if %errorlevel% neq 0 pause
