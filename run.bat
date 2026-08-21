@echo off
cd /d "%~dp0"
set QT_OPENGL=software
start /b pythonw main.py
exit