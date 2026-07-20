@echo off
set PYTHONHASHSEED=0
set PYTHONPATH=C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight\02_Technical
cd /d "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"
python -m pytest tests -q -p no:cacheprovider --tb=no -x > 02_Technical\tmp_pytest_out.txt 2>&1