@echo off
cd /d "C:\Users\1004\Desktop\stock market status"

echo ==== %date% %time% (close) ==== >> run_log.txt
python generate_close.py >> run_log.txt 2>&1

git add index.html data/state.json
git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo No changes, skip commit >> run_log.txt
) else (
    git commit -m "auto: close %date%" >> run_log.txt 2>&1
    git push >> run_log.txt 2>&1
)
