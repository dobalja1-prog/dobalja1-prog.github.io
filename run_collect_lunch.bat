@echo off
cd /d "C:\Users\1004\Desktop\stock market status"
echo ==== %date% %time% (collect lunch) ==== >> run_log.txt
python collect_lunch.py >> run_log.txt 2>&1
