@echo off
cd /d "C:\Users\1004\Desktop\stock market status"
echo ==== %date% %time% (collect close) ==== >> run_log.txt
"C:\Users\1004\AppData\Local\Programs\Python\Python312\python.exe" collect_close.py >> run_log.txt 2>&1
