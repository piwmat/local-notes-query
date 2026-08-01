@echo off
cd /d "%~dp0"
set "LLM_MODEL=gc/gemini-2.5-flash-lite"
"C:\Users\Mateusz\AppData\Local\anaconda3\python.exe" local-kb.py
pause
