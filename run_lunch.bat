@echo off
cd /d "C:\Users\1004\Desktop\stock market status"

echo ==== %date% %time% (lunch) ==== >> run_log.txt
python generate_lunch.py >> run_log.txt 2>&1

git add index.html data/state.json
git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo 변경 사항 없음, 커밋 생략 >> run_log.txt
) else (
    git commit -m "자동 생성: %date% 점심" >> run_log.txt 2>&1
    git push >> run_log.txt 2>&1
)
