@echo off
setlocal
REM ============================================================
REM OGIR Push + Sign-off launcher
REM
REM Runs the working git push command for the OGIR build branch.
REM The pre-push hook runs the closing-procedure gate (chain verify,
REM tests, SIGN_OFF block, handover log) automatically.
REM
REM Usage: double-click this file, or run from a terminal:
REM   launchers\Push-Signoff.bat
REM
REM Prerequisites:
REM   - The GitHub PAT is stored in Windows Credential Manager
REM     (cmdkey /generic:git:https://github.com /user:USERNAME /pass:PAT)
REM   - All commits are made locally (git add + git commit done)
REM   - The SIGN_OFF block is sealed to the chain
REM
REM If GCM hangs (system-level credential manager conflict), set
REM GIT_CONFIG_NOSYSTEM=1 before running this script, or run the
REM push manually with:
REM   git -c credential.helper=manager push origin ogir-build-2026-07-18
REM ============================================================

cd /d "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"

echo ============================================================
echo OGIR PUSH SIGN-OFF
echo ============================================================
echo.
echo Pushing branch ogir-build-2026-07-18 to origin...
echo The pre-push hook will run: chain verify, tests, SIGN_OFF check,
echo handover log check. All must PASS before the push proceeds.
echo.

REM Use the explicit credential helper so GCM finds the stored PAT
REM even when the system-level config is broken or hanging.
set GIT_TERMINAL_PROMPT=0
git -c credential.helper=manager push origin ogir-build-2026-07-18

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo PUSH FAILED. Common causes:
    echo   1. PAT not stored or expired. Re-store with:
    echo      cmdkey /generic:git:https://github.com /user:truthprojectofficial-max /pass:NEW_PAT
    echo   2. GCM hanging. Try with GIT_CONFIG_NOSYSTEM=1:
    echo      set GIT_CONFIG_NOSYSTEM=1
    echo      git -c credential.helper=manager push origin ogir-build-2026-07-18
    echo   3. Pre-push hook failed (chain/tests/SIGN_OFF). Fix the
    echo      failing check before pushing.
    echo ============================================================
    exit /b 1
)

echo.
echo ============================================================
echo PUSH SUCCEEDED.
echo ============================================================
pause