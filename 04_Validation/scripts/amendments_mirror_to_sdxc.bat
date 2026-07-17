@echo off
REM Mirror the post-amendment docs to the SDXC at D:\OrderGetItRight\
REM Re-derives the SDXC tree shape but does NOT touch the SDXC chain
REM (the SDXC chain is a copy of the laptop chain; the next mirror
REM  after the amendment seal will refresh it)
REM
REM 2026-07-16. Order Get It Right.

setlocal
set SRC=C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight
set DST=D:\OrderGetItRight

echo === Copying post-amendment docs to SDXC ===

robocopy "%SRC%\00_Strategy"        "%DST%\00_Strategy"        STRATEGY.md /R:0 /W:0
robocopy "%SRC%\04_Validation"      "%DST%\04_Validation"      MAINTENANCE_PLAN.txt STAGE_PAPER_DAILY.txt STAGE_PAPER_WEEKLY.txt STAGE_PAPER_MONTHLY.txt STAGE_PAPER_QUARTERLY.txt STAGE_PAPER_ANNUAL.txt YELLOW_RIBBON.md HANDOVER_TO_AUDITOR.md HANDOVER_TO_NEW_OPERATOR.md CONTEXT_WINDOW.md /R:0 /W:0
robocopy "%SRC%\04_Validation\scripts"  "%DST%\04_Validation\scripts"  phase_4_fingerprints.json /R:0 /W:0

echo === Verify both sides have the same SHA for each amended file ===
python -c "import hashlib,os; \
files = [ \
  '00_Strategy/STRATEGY.md', \
  '04_Validation/MAINTENANCE_PLAN.txt', \
  '04_Validation/STAGE_PAPER_WEEKLY.txt', \
  '04_Validation/STAGE_PAPER_QUARTERLY.txt', \
  '04_Validation/STAGE_PAPER_ANNUAL.txt', \
  '04_Validation/YELLOW_RIBBON.md', \
  '04_Validation/HANDOVER_TO_AUDITOR.md', \
  '04_Validation/HANDOVER_TO_NEW_OPERATOR.md', \
  '04_Validation/CONTEXT_WINDOW.md', \
  '04_Validation/scripts/phase_4_fingerprints.json', \
]; \
mismatch=0; \
for f in files: \
  a=hashlib.sha256(open(os.path.join(r'%SRC%',f),'rb').read()).hexdigest(); \
  b=hashlib.sha256(open(os.path.join(r'%DST%',f),'rb').read()).hexdigest(); \
  ok = (a==b); \
  print(('OK ' if ok else 'XX '), f, a, b); \
  if not ok: mismatch+=1; \
import sys; sys.exit(0 if mismatch==0 else 1)"

echo === Done ===
