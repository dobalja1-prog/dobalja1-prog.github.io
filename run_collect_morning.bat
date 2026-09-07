@echo off
cd /d "C:\Users\1004\Desktop\stock market status"
echo ==== %date% %time% (collect morning) ==== >> run_log.txt
python collect_morning.py >> run_log.txt 2>&1
