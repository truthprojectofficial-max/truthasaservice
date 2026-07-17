@echo off
REM SDXC re-burn: 2026-07-16
REM Operator: Justin Barnett
REM Purpose: bring D:\OrderGetItRight\ up to laptop state (2,797 blocks).
REM Step 1 of 2: backup current SDXC state to .bak-pre-2026-07-16-reburn\

robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight" "D:\OrderGetItRight.bak-pre-2026-07-16-reburn" /MIR /XD __pycache__ .pytest_cache target node_modules v
exit /b %ERRORLEVEL%
