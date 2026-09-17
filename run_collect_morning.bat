@echo off
cd /d "C:\Users\1004\Desktop\stock market status"
echo ==== %date% %time% (collect morning) ==== >> run_log.txt
"C:\Users\1004\AppData\Local\Programs\Python\Python312\python.exe" collect_morning.py >> run_log.txt 2>&1
