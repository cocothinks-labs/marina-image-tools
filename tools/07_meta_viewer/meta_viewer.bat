@echo off
chcp 65001 >nul
title Meta Viewer — Metadatos ComfyUI
pythonw "%~dp0meta_viewer.py" %*
