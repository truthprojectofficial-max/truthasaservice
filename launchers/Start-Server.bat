@echo off
setlocal
cd /d "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\\02_Technical"
"C:\Python314\python.exe" -m uvicorn src.server.app:app --host 127.0.0.1 --port 3000

