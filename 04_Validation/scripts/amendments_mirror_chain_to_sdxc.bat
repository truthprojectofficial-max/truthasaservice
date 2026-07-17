@echo off
REM Mirror the post-amendment laptop chain to the SDXC.
REM
REM The laptop chain is the source of truth. The SDXC chain is
REM a copy. After the laptop chain grows (e.g. the two amendment
REM seals at blocks 2798 + 2799), the SDXC must be re-synced.
REM
REM Uses robocopy /MIR on the 02_Technical/03_Vault/ folder only.
REM Does NOT touch 02_Technical/src/ (the source tree is unchanged
REM by the amendment) and does NOT touch 04_Validation/ (that was
REM already mirrored by amendments_mirror_to_sdxc.bat).
REM
REM 2026-07-16. Order Get It Right.

setlocal
set SRC=C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical\03_Vault
set DST=D:\OrderGetItRight\02_Technical\03_Vault

echo === Backing up SDXC chain ===
if exist "%DST%" (
    set BAK=%DST%.bak-pre-2026-07-16-amendment
    robocopy "%DST%" "%BAK%" /MIR /R:0 /W:0
)

echo === Mirroring laptop chain to SDXC ===
robocopy "%SRC%" "%DST%" /MIR /R:0 /W:0

echo === Verifying chain match ===
cd /d C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical
python -c "import sys, json, hashlib; \
src=open(r'C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical\03_Vault\facts_registry.json','rb').read(); \
dst=open(r'D:\OrderGetItRight\02_Technical\03_Vault\facts_registry.json','rb').read(); \
print('laptop bytes:', len(src), 'sha:', hashlib.sha256(src).hexdigest()[:16]); \
print('sdxc   bytes:', len(dst), 'sha:', hashlib.sha256(dst).hexdigest()[:16]); \
print('match:', src==dst)"

echo === Verify chain from SDXC ===
cd /d D:\OrderGetItRight\02_Technical
python -m src.verify_chain
