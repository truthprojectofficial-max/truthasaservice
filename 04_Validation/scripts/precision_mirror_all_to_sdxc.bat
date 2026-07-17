@echo off
REM Mirror all the post-precision docs to the SDXC.
REM 2026-07-16. Order Get It Right.

robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\00_Strategy" "D:\OrderGetItRight\00_Strategy" STRATEGY.md /R:0 /W:0
robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation" "D:\OrderGetItRight\04_Validation" MAINTENANCE_PLAN.txt STAGE_PAPER_WEEKLY.txt STAGE_PAPER_QUARTERLY.txt STAGE_PAPER_ANNUAL.txt YELLOW_RIBBON.md HANDOVER_TO_AUDITOR.md HANDOVER_TO_NEW_OPERATOR.md CONTEXT_WINDOW.md /R:0 /W:0
robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation\hardcopy" "D:\OrderGetItRight\04_Validation\hardcopy" QUICK_REFERENCE_CARD.txt /R:0 /W:0
