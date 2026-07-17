@echo off
REM Mirror the refreshed paper card and YELLOW_RIBBON to the SDXC.
REM 2026-07-16. Order Get It Right.

robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation\hardcopy" "D:\OrderGetItRight\04_Validation\hardcopy" QUICK_REFERENCE_CARD.txt /R:0 /W:0
robocopy "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\04_Validation" "D:\OrderGetItRight\04_Validation" YELLOW_RIBBON.md /R:0 /W:0
