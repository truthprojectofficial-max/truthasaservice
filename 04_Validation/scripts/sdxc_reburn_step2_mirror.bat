@echo off
REM SDXC re-burn: 2026-07-16, step 2
REM Operator: Justin Barnett
REM Purpose: mirror laptop state onto D:\OrderGetItRight\
REM Expected: SDXC chain root equals laptop chain root after the burn.
REM Expected: 3c33d6a18eee0c5935440ff2ebf9a3e675ab2297a2515f454493b1d972d140f5

robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight" "D:\OrderGetItRight" /MIR /XD __pycache__ .pytest_cache target node_modules v
exit /b %ERRORLEVEL%
